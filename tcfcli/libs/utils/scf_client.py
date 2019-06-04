import click
import json
from tcfcli.cmds.cli import __version__
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models
from tcfcli.common.user_config import UserConfig
from tcfcli.common.tcsam.tcsam_macro import TcSamMacro as tsmacro
from tcfcli.common.tcsam.tcsam_macro import TriggerMacro as trmacro
import base64


class ScfClient(object):

    CLOUD_API_REQ_TIMEOUT = 120
    def __init__(self):
        uc = UserConfig()
        self._cred = credential.Credential(secretId=uc.secret_id, secretKey=uc.secret_key)
        self._region = uc.region
        hp = HttpProfile(reqTimeout=ScfClient.CLOUD_API_REQ_TIMEOUT)
        cp = ClientProfile("TC3-HMAC-SHA256", hp)
        self._client = scf_client.ScfClient(self._cred, self._region, cp)
        self._client._sdkVersion = "TCFCLI"

    def get_function(self, function_name=None):
        req = models.GetFunctionRequest()
        req.FunctionName = function_name
        resp = self._client.GetFunction(req)
        return resp.to_json_string()

    def update_func_code(self, func, func_name, func_ns):
        req = models.UpdateFunctionCodeRequest()
        req.Namespace = func_ns
        req.FunctionName = func_name
        proper = func.get(tsmacro.Properties, {})
        req.Handler = proper.get(tsmacro.Handler)
        req.ZipFile = self._model_zip_file(proper.get(tsmacro.LocalZipFile))
        req.CosBucketName = proper.get(tsmacro.CosBucketName)
        req.CosObjectName = proper.get(tsmacro.CosObjectName)
        resp = self._client.UpdateFunctionCode(req)
        return resp.to_json_string()

    def update_func_config(self, func, func_name, func_ns):
        req = models.UpdateFunctionConfigurationRequest()
        req.Namespace = func_ns
        req.FunctionName = func_name
        proper = func.get(tsmacro.Properties, {})
        req.Description = proper.get(tsmacro.Desc)
        req.MemorySize = proper.get(tsmacro.MemSize)
        req.Timeout = proper.get(tsmacro.Timeout)
        req.Environment = self._model_envs(proper.get(tsmacro.Envi, {}))
        req.VpcConfig = self._model_vpc(proper.get(tsmacro.VpcConfig))
        resp = self._client.UpdateFunctionConfiguration(req)
        return resp.to_json_string()

    def create_func(self, func, func_name, func_ns):
        req = models.CreateFunctionRequest()
        req.Namespace =  func_ns
        req.FunctionName = func_name
        proper = func.get(tsmacro.Properties, {})
        req.Handler = proper.get(tsmacro.Handler)
        req.Description = proper.get(tsmacro.Desc)
        req.MemorySize = proper.get(tsmacro.MemSize)
        req.Timeout = proper.get(tsmacro.Timeout)
        req.Runtime = proper.get(tsmacro.Runtime)
        if req.Runtime:
            req.Runtime = req.Runtime[0].upper() + req.Runtime[1:].lower()
        req.Environment = self._model_envs(proper.get(tsmacro.Envi, {}))
        req.VpcConfig = self._model_vpc(proper.get(tsmacro.VpcConfig))
        req.Code = self._model_code(proper.get(tsmacro.LocalZipFile),
                                    proper.get(tsmacro.CosBucketName),
                                    proper.get(tsmacro.CosObjectName))
        resp = self._client.CreateFunction(req)
        return resp.to_json_string()

    def deploy_func(self, func, func_name, func_ns, forced):
        try:
            self.create_func(func, func_name, func_ns)
            return
        except TencentCloudSDKException as err:
            if err.code in ["ResourceInUse.Function", "ResourceInUse.FunctionName"] and forced:
                pass
            else:
                return err
        click.secho("{ns} {name} already exists, update it now".format(ns=func_ns, name=func_name), fg="red")
        try:
            self.update_func_config(func, func_name, func_ns)
            self.update_func_code(func, func_name, func_ns)
        except TencentCloudSDKException as err:
            return err
        return

    def create_trigger(self, trigger, name, func_name, func_ns):
        req = models.CreateTriggerRequest()
        req.Namespace = func_ns
        req.FunctionName = func_name
        req.TriggerName = name
        trigger_type = trigger.get(tsmacro.Type, "")
        req.Type = trigger_type.lower()
        proper = trigger.get(tsmacro.Properties, {})
        if trigger_type == tsmacro.TrCOS and trmacro.Bucket in proper:
            req.TriggerName = proper[trmacro.Bucket]
        if trigger_type == tsmacro.TrCMQ and trmacro.Name in proper:
            req.TriggerName = proper[trmacro.Name]
        self._fill_trigger_req_desc(req, trigger_type, proper)
        enable = proper.get(trmacro.Enable)
        if isinstance(enable, bool):
            enable = ["CLOSE", "OPEN"][int(enable)]
        req.Enable = enable
        resp = self._client.CreateTrigger(req)
        click.secho(resp.to_json_string())
    
    @staticmethod
    def _fill_trigger_req_desc(req, t, proper):
        if t == tsmacro.TrTimer:
            desc = proper.get(trmacro.CronExp)
        elif t == tsmacro.TrApiGw:
            ir_flag = proper.get(trmacro.IntegratedResp, False)
            isIntegratedResponse = "TRUE" if ir_flag else "FALSE"
            desc = {
                "api": {
                    "authRequired": "FALSE",
                    "requestConfig": {
                        "method": proper.get(trmacro.HttpMethod, None)
                    },
                    "isIntegratedResponse": isIntegratedResponse
                },
                "service": {
                    "serviceName": "SCF_API_SERVICE"
                },
                "release": {
                    "environmentName": proper.get(trmacro.StageName, None)
                }
            }
            desc = json.dumps(desc, separators=(',', ':'))
        elif t == tsmacro.TrCMQ:
            #desc = proper.get(trmacro.Name, name)
            desc = None
        
        elif t == tsmacro.TrCOS:
            desc = {"event": proper.get(tsmacro.Events), "filter": proper.get(trmacro.Filter)}
            desc = json.dumps(desc, separators=(',', ':'))
        else:
            raise Exception("Invalid trigger type:{}".format(str(t)))
        req.TriggerDesc = desc



    def deploy_trigger(self, trigger, name, func_name, func_ns):
        try:
            self.create_trigger(trigger, name, func_name, func_ns)
        except TencentCloudSDKException as err:
            return err

    def deploy(self, func, func_name, func_ns, forced):
        err = self.deploy_func(func, func_name, func_ns, forced)
        if err:
            return err

    @staticmethod
    def _model_envs(environment):
        envs_array = []
        vari = environment.get(tsmacro.Vari, {})
        for k in vari:
            var = models.Variable()
            var.Key = k
            var.Value = vari[k]
            envs_array.append(var)
        envi = models.Environment()
        envi.Variables = envs_array
        return envi

    @staticmethod
    def _model_vpc(vpc_config):
        if vpc_config:
            vpc = models.VpcConfig()
            vpc.VpcId = vpc_config.get("VpcId", None)
            vpc.SubnetId = vpc_config.get("SubnetId", None)
            return vpc
        return None

    @staticmethod
    def _model_code(zip_file, cos_buk_name, cos_obj_name):
        code = models.Code()
        code.CosBucketName = cos_buk_name
        code.CosObjectName = cos_obj_name
        if zip_file:
            with open(zip_file, 'rb') as f:
                code.ZipFile = base64.b64encode(f.read()).decode('utf-8')
        return code

    @staticmethod
    def _model_zip_file(zip_file):
        if zip_file:
            with open(zip_file, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return None
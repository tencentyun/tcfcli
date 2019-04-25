import click
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models
from tcfcli.common.user_config import UserConfig
import base64


class ScfClient(object):

    def __init__(self):
        uc = UserConfig()
        self._cred = credential.Credential(secretId=uc.secret_id, secretKey=uc.secret_key)
        self._region = uc.region
        cp = ClientProfile("TC3-HMAC-SHA256")
        self._client = scf_client.ScfClient(self._cred, self._region, cp)

    def get_function(self, function_name=None):
        req = models.GetFunctionRequest()
        req.FunctionName = function_name
        resp = self._client.GetFunction(req)
        return resp.to_json_string()

    def update_func_code(self, func, func_name, func_ns):
        req = models.UpdateFunctionCodeRequest()
        req.Namespace = func_ns
        req.FunctionName = func_name
        req.Handler = getattr(func, "Handler", None)
        req.ZipFile = self._model_zip_file(getattr(func, "LocalZipFile", None))
        req.CosBucketName = getattr(func, "CosBucketName", None)
        req.CosObjectName = getattr(func, "CosObjectName", None)
        resp = self._client.UpdateFunctionCode(req)
        return resp.to_json_string()

    def update_func_config(self, func, func_name, func_ns):
        req = models.UpdateFunctionConfigurationRequest()
        req.Namespace = func_ns
        req.FunctionName = func_name
        req.Description = getattr(func, "Description", None)
        req.MemorySize = getattr(func, "MemorySize", None)
        req.Timeout = getattr(func, "Timeout", None)
        req.Runtime = getattr(func, "Runtime", None)
        req.Environment = self._model_envs(getattr(func, "Environment", None))
        req.VpcConfig = self._model_vpc(getattr(func, "VpcConfig", None))
        resp = self._client.UpdateFunctionConfiguration(req)
        return resp.to_json_string()

    def create_func(self, func, func_name, func_ns):
        req = models.CreateFunctionRequest()
        req.Namespace =  func_ns
        req.FunctionName = func_name
        req.Handler = getattr(func, "Handler", None)
        req.Description = getattr(func, "Description", None)
        req.MemorySize = getattr(func, "MemorySize", None)
        req.Timeout = getattr(func, "Timeout", None)
        req.Runtime = getattr(func,"Runtime", None)
        req.Environment = self._model_envs(getattr(func, "Environment", None))
        req.VpcConfig = self._model_vpc(getattr(func, "VpcConfig", None))
        req.Code = self._model_code(getattr(func, "LocalZipFile", None),
                                    getattr(func, "CosBucketName", None),
                                    getattr(func, "CosObjectName", None))
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
        req.Type = trigger.__class__.__name__.lower()
        trigger_desc = trigger.trigger_desc()
        if isinstance(trigger_desc, dict):
            trigger_desc = json.dumps(trigger_desc, separators=(',', ':'))
        req.TriggerDesc = trigger_desc
        req.Enable = getattr(trigger, "Enable", "OPEN")
        resp = self._client.CreateTrigger(req)
        click.secho(resp.to_json_string())

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
        if environment is None:
            return None
        envs_array = []
        for k, v in vars(environment).items():
            var = models.Variable()
            var.Key = k
            var.Value = v
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
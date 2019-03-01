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

    def create_function(self, function_name=None, handler=None, description=None, zip_file=None,
                        cos_bucket_name=None, cos_object_name=None, memory_size=None,
                        timeout=None, runtime=None, environment=None, vpc=None):
        req = models.CreateFunctionRequest()
        req.FunctionName = function_name
        req.Handler = handler
        req.Description = description
        req.MemorySize = memory_size
        req.Timeout = timeout
        req.Runtime = runtime
        req.Environment = environment
        req.VpcConfig = vpc
        code = models.Code()
        code.CosBucketName = cos_bucket_name
        code.CosObjectName = cos_object_name
        if zip_file:
            with open(zip_file, 'rb') as f:
                code.ZipFile = base64.b64encode(f.read()).decode('utf-8')
        req.Code = code
        resp = self._client.CreateFunction(req)
        return resp.to_json_string()

    def update_function_code(self, function_name=None, handler=None,
                             cos_bucket_name=None, cos_object_name=None, zip_file=None):
        req = models.UpdateFunctionCodeRequest()
        req.FunctionName = function_name
        req.Handler = handler
        req.CosBucketName = cos_bucket_name
        req.CosObjectName = cos_object_name
        if zip_file:
            with open(zip_file, 'rb') as f:
                req.ZipFile = base64.b64encode(f.read()).decode('utf-8')
        resp = self._client.UpdateFunctionCode(req)
        return resp.to_json_string()

    def update_function_configuration(self, function_name=None, description=None, memory_size=None, timeout=None,
                                      runtime=None, environment=None, vpc=None):
        req = models.UpdateFunctionConfigurationRequest()
        req.FunctionName = function_name
        req.Description = description
        req.MemorySize = memory_size
        req.Timeout = timeout
        req.Runtime = runtime
        req.Environment = environment
        req.VpcConfig = vpc
        resp = self._client.UpdateFunctionConfiguration(req)
        return resp.to_json_string()

    def deploy(self, func):
        envs = self._array_envs(func.environment)

        try:
            self.create_function(function_name=func.name, handler=func.handler, description=func.description,
                                 zip_file=func.zip_file, cos_bucket_name=func.cos_bucket_name,
                                 cos_object_name=func.cos_object_name, memory_size=func.memory, timeout=func.timeout,
                                 runtime=func.runtime, environment=envs, vpc=func.vpc)
        except TencentCloudSDKException as err:
            if err.code == "ResourceInUse.FunctionName":
                pass
            else:
                return err

        try:
            self.update_function_code(function_name=func.name, handler=func.handler,
                                      cos_bucket_name=func.cos_bucket_name,
                                      cos_object_name=func.cos_object_name, zip_file=func.zip_file)
            self.update_function_configuration(function_name=func.name, description=func.description,
                                               memory_size=func.memory, timeout=func.timeout, runtime=func.runtime,
                                               environment=envs, vpc=func.vpc)
        except TencentCloudSDKException as err:
            return err

        return

    @staticmethod
    def _array_envs(environment):
        if not environment:
            return None

        envs = environment.get('Variables', None)
        if not isinstance(envs, dict):
            raise TypeError('environment format in template is invalid')

        envs_array = []
        for k, v in envs.items():
            envs_array.append({'Key': k, 'Value': v})

        return {'Variables': envs_array}


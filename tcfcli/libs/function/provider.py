from collections import namedtuple


Function = namedtuple("Function", [
    "name",
    "runtime",
    "memory",
    "timeout",
    "handler",
    "codeuri",
    "description",
    "cos_bucket_name",
    "cos_object_name",
    "zip_file",
    "environment",
    "vpc",
])

ResourcesKey = ("Handler",
                "Runtime",
                "Codeuri",
                "FunctionName",
                "Description",
                "MemorySize",
                "Timeout",
                "Environment",
                "ZipFile",
                "CodeBucket",
                "CodeObject",
                "VpcConfig")

GlobalsKey = ("Handler",
              "Runtime",
              "Description",
              "MemorySize",
              "Timeout",
              "Environment",
              "VpcConfig")

TENCENT_FUNCTION_TYPE = "TencentCloud::Serverless::Function"


class FunctionProvider(object):
    def get(self, name):
        raise NotImplementedError("Not Implemented")

    def get_all(self):
        raise NotImplementedError("Not Implemented")

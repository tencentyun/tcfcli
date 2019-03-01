from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tcfcli.common.user_config import UserConfig
from tcfcli.common.user_exceptions import UploadToCosFailed


class CosClient(object):
    def __init__(self):
        uc = UserConfig()
        self._config = CosConfig(Secret_id=uc.secret_id, Secret_key=uc.secret_key,
                                 Region=uc.region, Appid=uc.appid)
        self._client = CosS3Client(self._config)

    def upload_file2cos(self, bucket, file, key):
        # save funcs in the func directory
        try:
            response = self._client.put_object(Bucket=bucket,
                                               Body=file,
                                               Key=key,
                                               Metadata={
                                                   'x-cos-acl': 'public-read',
                                                   'Content-Type': 'application/x-zip-compressed',
                                                })
            if not response['ETag']:
                raise UploadToCosFailed("Upload func package failed")
        except Exception as e:
            raise e

        codeuri_in_cos = bucket + '/' + key
        return codeuri_in_cos

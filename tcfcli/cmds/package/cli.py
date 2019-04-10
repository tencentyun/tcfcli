import os
import copy
import click
import uuid
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from tcfcli.libs.utils.yaml_parser import yaml_dump
from tcfcli.libs.function.context import Context
from tcfcli.libs.utils.cos_client import CosClient
from tcfcli.common.user_exceptions import TemplateNotFoundException, \
    InvalidTemplateException, ContextException
from tcfcli.libs.tcsam.tcsam import Resources

_DEFAULT_OUT_TEMPLATE_FILE = "deploy.yaml"
_CURRENT_DIR = '.'


@click.command()
@click.option('--template-file', '-t', type=click.Path(exists=True), help="FAM template file or path about function config")
@click.option('--cos-bucket', type=str, help="COS bucket name")
@click.option('--output-template-file', '-o',
              type=click.Path(),
              help="FAM output template file or path",
              default=_DEFAULT_OUT_TEMPLATE_FILE,
              show_default=True)
def package(template_file, cos_bucket, output_template_file):
    '''
    Package a scf and upload to the cos
    '''
    package = Package(template_file, cos_bucket, output_template_file)
    package.do_package()


class Package(object):

    def __init__(self, template_file, cos_bucket, output_template_file):
        self.template_file = template_file
        self.cos_bucket = cos_bucket
        self.output_template_file = output_template_file
        self.check_params()
        self.resource = Resources(Context.get_template_data(self.template_file))

    def do_package(self):
        for ns_name, ns in vars(self.resource).items():
            for func_name, func in vars(ns).items():
                code_url = self._do_package_core(getattr(func, "CodeUri", ""))
                if "cos_bucket_name" in code_url:
                    setattr(func, "CosBucketName", code_url["cos_bucket_name"])
                    setattr(func, "CosObjectName", code_url["CosObjectName"])
                    click.secho("Upload function zip file '{}' to COS bucket '{}' success".
                                format(os.path.basename(code_url["cos_object_name"]),
                                       code_url["cos_bucket_name"]), fg="green")
                elif "zip_file" in code_url:
                    setattr(func, "LocalZipFile", code_url["zip_file"])

        yaml_dump(self.resource.to_json(), self.output_template_file)
        click.secho("Generate deploy file '{}' success".format(self.output_template_file), fg="green")

    def check_params(self):
        if not self.template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file".format(self.template_file))

    def _do_package_core(self, func_path):
        zipfile, zip_file_name = self._zip_func(func_path)
        code_url = dict()
        if self.cos_bucket:
            CosClient().upload_file2cos(bucket=self.cos_bucket, file=zipfile.read(),
                                        key=zip_file_name)
            code_url["cos_bucket_name"] = self.cos_bucket
            code_url["cos_object_name"] = "/" + zip_file_name
        else:
            code_url["zip_file"] = os.path.join(os.getcwd(), zip_file_name)

        return code_url

    def _zip_func(self, func_path):
        buff = BytesIO()
        if not os.path.exists(func_path):
            raise ContextException("Function file or path not found by CodeUri '{}'".format(func_path))

        zip_file_name = str(uuid.uuid1()) + '.zip'
        cwd = os.getcwd()
        os.chdir(func_path)
        with ZipFile(buff, mode='w', compression=ZIP_DEFLATED) as zip_object:
            for current_path, sub_folders, files_name in os.walk(_CURRENT_DIR):
                for file in files_name:
                    zip_object.write(os.path.join(current_path, file))

        os.chdir(cwd)
        buff.seek(0)
        buff.name = zip_file_name

        # a temporary support for upload func from local zipfile
        with open(zip_file_name, 'wb') as f:
            f.write(buff.read())
            buff.seek(0)
        # click.secho("Compress function '{}' to zipfile '{}' success".format(func_config.name, zip_file_name))

        return buff, zip_file_name

    def _get_code_abs_path(self, code_uri):

        if not self._cwd or self._cwd == _CURRENT_DIR:
            self._cwd = os.getcwd()

        self._cwd = os.path.abspath(self._cwd)

        code_path = code_uri
        if not os.path.isabs(code_uri):
            code_path = os.path.normpath(os.path.join(self._cwd, code_path))

        return code_path

    def _get_cwd(self):
        cwd = os.path.dirname(os.path.abspath(self._template_path))
        return cwd

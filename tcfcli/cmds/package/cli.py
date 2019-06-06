import os
import copy
import click
import uuid
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from tcfcli.libs.utils.yaml_parser import yaml_dump
from tcfcli.common.template import Template
from tcfcli.libs.utils.cos_client import CosClient
from tcfcli.common.user_exceptions import TemplateNotFoundException, \
    InvalidTemplateException, ContextException
from tcfcli.common.tcsam.tcsam_macro import TcSamMacro as tsmacro
from tcfcli.common import tcsam

_DEFAULT_OUT_TEMPLATE_FILE = "deploy.yaml"
_CURRENT_DIR = '.'
_BUILD_DIR = './.tcf_build'


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

        # self.resource = Resources(Template.get_template_data(self.template_file))
        template_data = tcsam.tcsam_validate(Template.get_template_data(self.template_file))
        self.resource = template_data.get(tsmacro.Resources, {})

    def do_package(self):
        for ns in  self.resource:
            for func in  self.resource[ns]:
                if func == tsmacro.Type:
                    continue
                code_url = self._do_package_core(
                    self.resource[ns][func][tsmacro.Properties].get(tsmacro.CodeUri, "")
                )
                if "cos_bucket_name" in code_url:
                    self.resource[ns][func][tsmacro.Properties]["CosBucketName"] = code_url["cos_bucket_name"]
                    self.resource[ns][func][tsmacro.Properties]["CosObjectName"] = code_url["CosObjectName"]
                    click.secho("Upload function zip file '{}' to COS bucket '{}' success".
                                format(os.path.basename(code_url["cos_object_name"]),
                                       code_url["cos_bucket_name"]), fg="green")
                elif "zip_file" in code_url:
                    self.resource[ns][func][tsmacro.Properties]["LocalZipFile"] = code_url["zip_file"]

        yaml_dump({tsmacro.Resources: self.resource}, self.output_template_file)
        click.secho("Generate deploy file '{}' success".format(self.output_template_file), fg="green")

    def check_params(self):
        if not self.template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file")

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
                if current_path == _BUILD_DIR:
                    continue
                for file in files_name:
                    zip_object.write(os.path.join(current_path, file))

        os.chdir(cwd)
        buff.seek(0)
        buff.name = zip_file_name

        
        if not os.path.exists(_BUILD_DIR):
            os.mkdir(_BUILD_DIR)
        zip_file_name = os.path.join(_BUILD_DIR, zip_file_name)
        # a temporary support for upload func from local zipfile
        with open(zip_file_name, 'wb') as f:
            f.write(buff.read())
            buff.seek(0)
        # click.secho("Compress function '{}' to zipfile '{}' success".format(func_config.name, zip_file_name))

        return buff, zip_file_name
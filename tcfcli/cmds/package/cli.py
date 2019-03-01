import os
import click
import uuid
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from tcfcli.libs.utils.yaml_parser import yaml_dump
from tcfcli.libs.function.context import Context
from tcfcli.libs.utils.cos_client import CosClient
from tcfcli.common.user_exceptions import TemplateNotFoundException, \
    InvalidTemplateException, ContextException

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
    Package.check_params(template_file)

    try:
        with Context(template_file=template_file, cos_bucket=cos_bucket, output_template_file=output_template_file) \
                as pkg_ctx:
            Package(pkg_ctx).do_package()
    except InvalidTemplateException as e:
        raise e


class Package(object):
    def __init__(self, pkg_ctx):
        self._pkg_ctx = pkg_ctx
        self._template_path = pkg_ctx.template_path
        self._cwd = self._get_cwd()

    def do_package(self):
        deploy_template_dict = self._pkg_ctx.deploy_template
        deploy_file_path = self._pkg_ctx.output_template_file_path

        for func in self._pkg_ctx.get_functions():
            code_url = self._do_package_core(func)
            if "cos_bucket_name" in code_url:
                deploy_template_dict["Resources"][func.name]["Properties"]["CosBucketName"] = code_url["cos_bucket_name"]
                deploy_template_dict["Resources"][func.name]["Properties"]["CosObjectName"] = code_url["cos_object_name"]
                click.secho("Upload function zip file '{}' to COS bucket '{}' success".
                            format(os.path.basename(code_url["cos_object_name"]),
                                   code_url["cos_bucket_name"]), fg="green")
            elif "zip_file" in code_url:
                deploy_template_dict["Resources"][func.name]["Properties"]["LocalZipFile"] = code_url["zip_file"]
        yaml_dump(deploy_template_dict, deploy_file_path)
        click.secho("Generate deploy file '{}' success".format(deploy_file_path), fg="green")

    @staticmethod
    def check_params(template_file):
        if not template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file".format(template_file))

    def _do_package_core(self, func_config):
        zipfile, zip_file_name = self._zip_func(func_config)
        code_url = dict()
        if self._pkg_ctx.cos_bucket:
            CosClient().upload_file2cos(bucket=self._pkg_ctx.cos_bucket, file=zipfile.read(),
                                        key=zip_file_name)
            code_url["cos_bucket_name"] = self._pkg_ctx.cos_bucket
            code_url["cos_object_name"] = "/" + zip_file_name
        else:
            code_url["zip_file"] = os.path.join(os.getcwd(), zip_file_name)

        return code_url

    def _zip_func(self, func_config):
        buff = BytesIO()
        func_path = self._get_code_abs_path(func_config.codeuri)
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

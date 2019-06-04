from .tcsam_macro import TcSamMacro as macro

class TcSamutil(object):

    @staticmethod
    def merge_globals(tcsam_data):
        resources = tcsam_data.get(macro.Resources, {})
        glob = tcsam_data.get(macro.Globals, {})
        glob_func_proper = glob.get(macro.Function, {})

        if glob_func_proper is None:
            return

        for func in TcSamutil._iter_func(resources):
            if macro.Properties not in func:
                continue
            if func[macro.Properties] is None:
                func[macro.Properties] = {}
            for pro in glob_func_proper:
                if pro not in func[macro.Properties] or not func[macro.Properties][pro]:
                    func[macro.Properties][pro] = glob_func_proper[pro]



    @staticmethod
    def _iter_func(resources):
        for ns in resources:
            if resources[ns] is None:
                continue
            for func in resources[ns]:
                if func == macro.Type or resources[ns][func] is None:
                    continue
                yield resources[ns][func]

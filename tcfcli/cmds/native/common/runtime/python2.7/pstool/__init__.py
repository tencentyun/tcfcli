import platform
sysstr = platform.system()


__all__ = ['get_peak_memory']



def get_peak_memory():
    try:
        if sysstr.lower() == "windows":
            from .winps import win_peak_memory
            return win_peak_memory()
        import resource

        if sysstr.lower() == "darwin":
            return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**20))
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))
    except Exception as err:
        print("get memory info failed, {}".format(str(err)))
        return 0



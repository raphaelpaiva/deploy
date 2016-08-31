import requests

import jbosscli

OK_RET_CODE = 0
ERROR_RET_CODE = 1


def generate_test_list(args):
    controller = jbosscli.Jbosscli(args.controller, args.auth)

    base_url = args.base_url if args.base_url \
        else args.controller.split(":")[0]

    assigned_deployments = controller.get_assigned_deployments()

    modules = [x for x in assigned_deployments if x.enabled and
               ".jar" not in x.runtime_name]

    error_modules = []

    for module in modules:
        app = controller.fecth_context_root(module)
        url = "http://{0}{1}".format(base_url, app)
        r = requests.get(url)

        if r.status_code >= 400:
            error_modules.append(url + " " + str(r.status_code))

    output = ""
    return_code = None
    if error_modules:
        output += "Some modules were inaccessible:\n"
        output += "\n".join(error_modules)
        return_code = ERROR_RET_CODE
    else:
        output += "OK!"
        return_code = OK_RET_CODE

    return (output, return_code, "")

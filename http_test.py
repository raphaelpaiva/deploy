import requests

import jbosscli

def generate_test_list(args):
    controller = jbosscli.Jbosscli(args.controller, args.auth)

    base_url = args.base_url if args.base_url else args.controller.split(":")[0]

    assigned_deployments = controller.get_assigned_deployments()

    modules = [x for x in assigned_deployments if x.enabled and ".jar" not in x.runtime_name]

    output = ""

    for module in modules:
        app = controller.fecth_context_root(module)
        url = "http://{0}{1}".format(base_url, app)
        r = requests.get(url)
        output += url + " " + str(r.status_code) + "\n"

    return output

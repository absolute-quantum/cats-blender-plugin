import json
import urllib
from collections import OrderedDict


update_in_process = False


version_list = None
current_version = None
update_needed = False


# TODO
def check_for_update_background(bl_info):
    print('START UPDATE CHECK')
    global current_version, update_needed
    current_version = bl_info['version']

    get_github_tags()

    update_needed = check_for_update_available()
    if not update_needed:
        print('NO UPDATE NEEDED')




def get_github_tags():
    print('GET RELEASES')
    global version_list
    try:
        with urllib.request.urlopen("https://api.github.com/repos/michaeldegroot/cats-blender-plugin/releases") as url:
            data = json.loads(url.read().decode())
    except urllib.error.URLError:
        print('URL ERROR')
        return False

    version_list = OrderedDict
    for version in data:
        version_list[version['name']] = version['zipball_url']

    print(version_list)


def check_for_update_available():
    if not version_list:
        return False

    latest_version = version_list.keys()[0]
    if latest_version > current_version:
        return True







class GithubEngine(object):

    def __init__(self):
        self.api_url = 'https://api.github.com'
        self.token = None
        self.name = "github"

    def form_repo_url(self, updater):
        return "{}{}{}{}{}".format(self.api_url, "/repos/", updater.user, "/", updater.repo)

    def form_tags_url(self, updater):
        if updater.use_releases:
            return "{}{}".format(self.form_repo_url(updater), "/releases")
        else:
            return "{}{}".format(self.form_repo_url(updater), "/tags")

    def form_branch_list_url(self, updater):
        return "{}{}".format(self.form_repo_url(updater), "/branches")

    def form_branch_url(self, branch, updater):
        return "{}{}{}".format(self.form_repo_url(updater),
                               "/zipball/", branch)

    def parse_tags(self, response, updater):
        if response == None:
            return []
        return response




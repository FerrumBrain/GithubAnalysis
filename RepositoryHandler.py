import re
import json
import pydriller
from itertools import chain, combinations


def _powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def _is_github_link(link):
    pattern = r'(?:git|https?|git@)(?:\:\/\/)?github.com[/|:][A-Za-z0-9-]+?\/[\w\.-]+?\.git(?:\/?|\#[\w\.\-_]+)?$'
    res = bool(re.match(pattern, link))
    return res


def init_repository_handler(link):
    return _RepositoryHandler(link) if _is_github_link(link) else None


class _RepositoryHandler:
    def __init__(self, link):
        assert _is_github_link(link)

        self._collect_statistics = {
            "groups_of_developers_files": self._get_groups_of_developers_files,
            "groups_of_developers_modules": self._get_groups_of_developers_modules,
            "groups_of_files": self._get_groups_of_files
        }

        repo = pydriller.Repository(link)
        json_path = 'settings.json'
        with open(json_path, 'r') as settings_file:
            args = json.load(settings_file)
        self.args = args["statistics"]
        self.sufficiency_for_considering = args["sufficiency_for_considering"]

        self.authors_by_files = {}
        self.authors_by_modules = {}
        self.files_by_commits = []
        for commit in repo.traverse_commits():
            files = []
            for file in commit.modified_files:
                # If file was moved, it is still the same file
                if file.old_path is not None and file.new_path is not None and file.old_path != file.new_path:
                    self.authors_by_files[file.new_path] = self.authors_by_files[file.old_path]
                    self.authors_by_files[file.old_path] = {}
                    for i in range(len(self.files_by_commits)):
                        for j in range(len(self.files_by_commits[i])):
                            if self.files_by_commits[i][j] == file.old_path:
                                self.files_by_commits[i][j] = file.new_path

                if file.new_path not in self.authors_by_files.keys():
                    self.authors_by_files[file.new_path] = {}
                if commit.author.name not in self.authors_by_files[file.new_path].keys():
                    self.authors_by_files[file.new_path][commit.author.name] = 0
                self.authors_by_files[file.new_path][commit.author.name] += 1
                path = file.new_path if file.new_path is not None else file.old_path

                files.append(path)

                # Each directory is a module
                cur = ""
                for module in path.split('/')[:-1]:
                    cur += module + "/"
                    if cur not in self.authors_by_modules.keys():
                        self.authors_by_modules[cur] = {}
                    if commit.author.name not in self.authors_by_modules[cur].keys():
                        self.authors_by_modules[cur][commit.author.name] = 0
                    self.authors_by_modules[cur][commit.author.name] += 1
            self.files_by_commits.append(files)

    # Groups of developers who most frequently contribute together are defined as following:
    # 1) List of top-frequent contributors is defined for each file
    # 2) Each subgroup of this list gets a point for
    # 3) Subgroups with the most number of points are desired ones
    def _get_groups_of_developers_files(self):
        top_authors_by_files = {file: list(map(lambda n_author: n_author[1], list(
            filter(lambda n_author: n_author[0] >= self.sufficiency_for_considering * max(
                self.authors_by_files[file].values()),
                   [(self.authors_by_files[file][author], author) for author in self.authors_by_files[file].keys()]))))
                                for file in self.authors_by_files.keys()}
        res = {}
        for file in top_authors_by_files.keys():
            for subset in _powerset(top_authors_by_files[file]):
                if len(subset) < 2:
                    continue
                if subset not in res.keys():
                    res[subset] = 0
                res[subset] += 1
        groups = [group_points[1] for group_points in sorted([(res[group], group) for group in res.keys()])[-5:]]
        return groups

    def _get_groups_of_developers_modules(self):
        top_authors_by_modules = {module: list(map(lambda n_author: n_author[1], list(
            filter(lambda n_author: n_author[0] >= self.sufficiency_for_considering * max(
                self.authors_by_modules[module].values()),
                   [(self.authors_by_modules[module][author], author) for author in
                    self.authors_by_modules[module].keys()]))))
                                  for module in self.authors_by_modules.keys()}
        res = {}
        for module in top_authors_by_modules.keys():
            for subset in _powerset(top_authors_by_modules[module]):
                if len(subset) < 2:
                    continue
                if subset not in res.keys():
                    res[subset] = 0
                res[subset] += 1
        groups = [group_points[1] for group_points in sorted([(res[group], group) for group in res.keys()])[-5:]]
        return groups

    def _get_groups_of_files(self):
        files = list(set(chain.from_iterable(self.files_by_commits)))
        res = {subset: len(list(
            filter(lambda files_list: len([f for f in subset if f in files_list]) == len(subset) and len(subset) > 1,
                   self.files_by_commits))) for subset in _powerset(files)}
        sorted_values = sorted(list(set(res.values())))
        top5_value = sorted_values[
            -5 if len(sorted_values) >= 5 else 1]  # Not 0 so we can avoid empty set and one-element sets
        return list(filter(lambda subset: res[subset] >= top5_value, res.keys()))

    def get_statistics(self):
        difference = set(self.args) - set(self._collect_statistics.keys())
        if len(difference) != 0:
            raise NotImplementedError(f"No implementation for {', '.join(list(difference))}")
        return {statistics_name: self._collect_statistics[statistics_name]() for statistics_name in self.args}

# /usr/bin/env python
# -*- coding: utf-8 -*-

from loguru import logger
import git
from git import Repo
from typing import Union
from pathlib import Path


def repo_status_to_dict(repodir:Union[Path, str], reponame:str=None):
    repodir = Path(repodir)
    if is_git_repo(str(repodir)):
        repo = Repo(str(repodir))
    else:
        return {}

    if reponame is None:
        reponame = repodir.resolve().stem

    dirty = repo.is_dirty()
    retval = {
        f"repo {reponame} id": repo.head.object.hexsha,
        f"repo {reponame} is dirty": dirty,
    }
    if dirty:
        dirty_files = ",".join([item.a_path for item in repo.index.diff(None)])
        retval[f"repo {reponame} dirty files"] = dirty_files

    try:
        describe = repo.git.describe()
        retval[f"repo {reponame} describe"] = describe
    except git.exc.GitCommandError as e:
        logger.info(f"git describe error: {str(e)}")
    return retval


def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

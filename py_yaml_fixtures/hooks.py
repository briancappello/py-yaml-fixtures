# this file is for Flask Unchained

import os

from flask_unchained import AppFactoryHook, Bundle

from .fixtures_loader import MULTI_CLASS_FILENAMES


class ModelFixtureFoldersHook(AppFactoryHook):
    """
    Determines the bundle folder to load database fixtures from (if any).
    """
    # we implement this hook only for fixtures folder name customization purposes

    bundle_module_name = 'fixtures'
    bundle_override_module_name_attr = 'fixtures_folder_name'
    name = 'model_fixture_folders'
    run_after = ['models']
    run_before = ['init_extensions']

    def run_hook(self, *args, **kwargs):
        pass  # noop

    @classmethod
    def get_fixtures_dirs(cls, bundle: Bundle):
        folder_name = getattr(bundle,
                              cls.bundle_override_module_name_attr,
                              cls.bundle_module_name)
        if not folder_name:
            return []

        bundle_dir = None
        for filename in MULTI_CLASS_FILENAMES:
            if os.path.exists(os.path.join(bundle.folder, filename)):
                bundle_dir = bundle.folder

        fixtures_dir = os.path.join(bundle.folder, folder_name)
        if not os.path.exists(fixtures_dir):
            fixtures_dir = None

        return [x for x in [bundle_dir, fixtures_dir] if x]


__all__ = [
    'ModelFixtureFoldersHook',
]

import logging
import os
import posixpath
import types
import urllib.parse
import re
import mkdocs.plugins
import mkdocs

from material.plugins.blog.plugin import BlogPlugin
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.structure.nav import Section
from mkdocs.plugins import PrefixedLogger, event_priority
from mkdocs.structure.files import InclusionLevel, Files
from material.plugins.blog.structure import Category, Post, View, Excerpt, Archive

members_ids = {
    'Jiheon': '5fb309bc7489a576484431ba8338807e',  # jh
    'Hayoung': '67b4c6fb2220ac6705aa97046f3503a1',  # hy
    'Chaeyoung': '65eff6ab044ae8dea6816794f11a6fc1',  # cy
    'Jiwon': '6599dbbcaa26237c2ab0f3becb421b45',  # jw
    'Jisun': '01435f74a49ba8a519705ad242348232',  # js
    'Saerom': '326c0d1e7045798aa3964e2028c34628',  # sr
    'Seoyeon': '56bdfafb606d9ce1b4ecdd572595e242',  # sy
    'Nagyung': '5477d46be848bd40252f9d13ef62cb4d',  # ng
    'Gyuri': 'db56036fc59a94a9ef617261c90c783f'  # gr
}

ids_to_name = {v: k for k, v in members_ids.items()}

class CustomView(View):
    type = 'CustomView'
    pass

def on_config(config: MkDocsConfig):
    blog_plugins: list[tuple[str, BlogPlugin]] = [(name, p) for name, p in config.plugins.items() if isinstance(p, BlogPlugin)]

    for blog_name, blog in blog_plugins:
        blog._generate_categories = types.MethodType(patch_generate_categories, blog)

    patch_event('files', patch_on_files, config)
    # patch_event('nav', patch_on_nav, config)

def patch_event(name, func, config):
    for i, event in enumerate(config.plugins.events[name]):
        if hasattr(event, "__self__"):
            if isinstance(event.__self__, BlogPlugin):
                config.plugins.events[name][i] = types.MethodType(func, event.__self__)
                print(f'Patching {event.__self__} {func}')


def patch_on_files(self: BlogPlugin, files, *, config):
    print(f'sort_posts_latest Running patch_on_files {self}')
    if not self.config.enabled:
        return

    # Resolve path to entrypoint and site directory
    root = posixpath.normpath(self.config.blog_dir)
    site = config.site_dir

    # Compute and normalize path to posts directory
    path = self.config.post_dir.format(blog=root)
    path = posixpath.normpath(path)

    # Adjust destination paths for media files
    for file in files.media_files():
        if not file.src_uri.startswith(path):
            continue

        # We need to adjust destination paths for assets to remove the
        # purely functional posts directory prefix when building
        file.dest_uri = file.dest_uri.replace(path, root)
        file.abs_dest_path = os.path.join(site, file.dest_path)
        file.url = file.url.replace(path, root)

    # Resolve entrypoint and posts sorted by descending date - if the posts
    # directory or entrypoint do not exist, they are automatically created
    self.blog = self._resolve(files, config)
    self.blog.posts = sorted(
        self._resolve_posts(files, config),
        key=lambda post: post.config.date.created,
        # reverse=True # @CHANGE: Disable sorting in reverse order
    )

    # Generate views for archive
    if self.config.archive:
        self.blog.views.extend(
            self._generate_archive(config, files)
        )

    # Generate views for categories
    if self.config.categories:
        self.blog.views.extend(sorted(
            self._generate_categories(config, files),
            key=lambda view: view.name,
            reverse=False
        ))

    # Generate pages for views
    if self.config.pagination:
        for view in self._resolve_views(self.blog):
            for page in self._generate_pages(view, config, files):
                view.pages.append(page)

    # Ensure that entrypoint is always included in navigation
    self.blog.file.inclusion = InclusionLevel.INCLUDED

def patch_generate_categories(self, config: MkDocsConfig, files: Files):
    for post in self.blog.posts:
        authors = post.meta['authors'] if 'authors' in post.meta else []

        for author_cat in post.config.categories:
            name = f'Comments'
            path = self._format_path_for_category(f'{author_cat} {name}')
            if author_cat in members_ids.keys():
                yield from make_file(name, post, self, files, path, config, CustomView, author_cat)

        for author_name, author_id in members_ids.items():
            # print(post.meta)
            # print('authors', post.authors)

            if len(authors) == 0:
                continue

            main_author = authors[0]

            if main_author != author_id:
                continue

            if tags := post.meta.get('tags'):
                # print('my tags', tags)
                if 'Artist Post' in tags:
                    name = f'Artist Posts'
                    path = self._format_path_for_category(f'{author_name} {name}')
                    yield from make_file(name, post, self, files, path, config, CustomView, ids_to_name[main_author])

                if 'Moment' in tags:
                    name = f'Moments'
                    path = self._format_path_for_category(f'{author_name} {name}')
                    yield from make_file(name, post, self, files, path, config, CustomView, ids_to_name[main_author])

def make_file(name, post, blog, files, path, config, type, data):
    categories = blog.config.categories_allowed or [name]
    if name not in categories:
        docs = os.path.relpath(config.docs_dir)
        path = os.path.relpath(post.file.abs_src_path, docs)
        raise PluginError(f"Error reading categories of post '{path}' in "
                          f"'{docs}': category '{name}' not in allow list")

    # Create file for view, if it does not exist
    file = files.get_file_from_path(path)
    if not file or blog.temp_dir not in file.abs_src_path:
        file = blog._path_to_file(path, config)
        files.append(file)

        # Create file in temporary directory and temporarily remove
        # from navigation, as we'll add it at a specific location
        blog._save_to_file(file.abs_src_path, f"# {name}")
        file.inclusion = InclusionLevel.EXCLUDED

    # Create and yield view
    if not isinstance(file.page, type):
        view = type(name, file, config)
        view.type = data
        yield view #type(name, file, config)

    file.page.posts.append(post)


HOOK_NAME: str = "sort_posts_latest"
"""Name of this hook. Used in logging."""

LOG: PrefixedLogger = PrefixedLogger(HOOK_NAME, logging.getLogger(f"mkdocs.hooks.{HOOK_NAME}"))
"""Logger instance for this hook."""

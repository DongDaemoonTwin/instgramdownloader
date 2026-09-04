import os
from pathlib import Path
import instaloader


def save_caption(folder, post):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'caption.txt').write_text(post.caption or '', encoding='utf-8')


def main():
    target = input('Instagram URL or username: ').strip().replace('@','')
    out = Path('downloads')
    loader = instaloader.Instaloader(
        dirname_pattern=str(out / '{profile}' / '{date_utc:%Y-%m-%d}_{shortcode}'),
        filename_pattern='{shortcode}',
        download_comments=False,
        save_metadata=False
    )

    if '/p/' in target or '/reel/' in target:
        code = target.rstrip('/').split('/')[-1]
        post = instaloader.Post.from_shortcode(loader.context, code)
        loader.download_post(post, target=post.owner_username)
        save_caption(out / post.owner_username / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}', post)
    else:
        profile = instaloader.Profile.from_username(loader.context, target)
        for post in profile.get_posts():
            loader.download_post(post, target=target)
            save_caption(out / target / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}', post)


if __name__ == '__main__':
    main()

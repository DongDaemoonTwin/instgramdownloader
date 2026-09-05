import os
import shutil
import zipfile
from pathlib import Path

import instaloader


def save_caption(folder, post):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'caption.txt').write_text(post.caption or '', encoding='utf-8')


def get_output_folder():
    return Path(os.getenv('OUTPUT_DIR', 'downloads')).expanduser()


def make_zip(source_folder):
    """Create a zip file that can be downloaded from Codespace."""
    source_folder = Path(source_folder)
    if not source_folder.exists():
        return None

    zip_path = Path('instagram_backup.zip')

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in source_folder.rglob('*'):
            if file.is_file():
                z.write(file, file.relative_to(source_folder.parent))

    return zip_path


def main():
    target = input('Instagram URL or username: ').strip().replace('@', '')

    out = get_output_folder()
    out.mkdir(parents=True, exist_ok=True)

    print(f'저장 위치: {out.resolve()}')

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
        save_caption(
            out / post.owner_username / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}',
            post,
        )
    else:
        profile = instaloader.Profile.from_username(loader.context, target)
        for post in profile.get_posts():
            loader.download_post(post, target=target)
            save_caption(
                out / target / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}',
                post,
            )

    print('\n다운로드 완료')

    zip_file = make_zip(out)
    if zip_file:
        print('\n=================================')
        print('PC로 가져가기 준비 완료')
        print(f'파일: {zip_file.resolve()}')
        print('Codespace 파일 탐색기에서 instagram_backup.zip 을 우클릭 → Download 하세요.')
        print('=================================')


if __name__ == '__main__':
    main()

import os
import time
import zipfile
from pathlib import Path
from itertools import islice

import instaloader


def save_caption(folder, post):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'caption.txt').write_text(post.caption or '', encoding='utf-8')


def get_output_folder():
    return Path(os.getenv('OUTPUT_DIR', 'downloads')).expanduser()


def make_zip(source_folder):
    zip_path = Path('instagram_backup.zip')
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in Path(source_folder).rglob('*'):
            if file.is_file():
                z.write(file, file.relative_to(Path(source_folder).parent))

    return zip_path


def create_loader():
    loader = instaloader.Instaloader(
        dirname_pattern=str(get_output_folder() / '{profile}' / '{date_utc:%Y-%m-%d}_{shortcode}'),
        filename_pattern='{shortcode}',
        download_comments=False,
        save_metadata=False,
    )

    login = os.getenv('INSTAGRAM_LOGIN')
    if login:
        try:
            loader.load_session_from_file(login)
            print(f'저장된 로그인 세션 사용: @{login}')
        except FileNotFoundError:
            password = input(f'Instagram @{login} password: ')
            loader.login(login, password)
            loader.save_session_to_file()
            print('로그인 세션 저장 완료')

    return loader


def main():
    target = input('Instagram URL or username: ').strip().replace('@', '')

    out = get_output_folder()
    out.mkdir(parents=True, exist_ok=True)

    loader = create_loader()
    print(f'저장 위치: {out.resolve()}')

    try:
        if '/p/' in target or '/reel/' in target:
            code = target.rstrip('/').split('/')[-1]
            post = instaloader.Post.from_shortcode(loader.context, code)
            loader.download_post(post, target=post.owner_username)
            save_caption(out / post.owner_username / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}', post)
        else:
            limit_input = input('다운로드할 게시물 개수 (기본 10개): ').strip()
            limit = int(limit_input) if limit_input else 10

            profile = instaloader.Profile.from_username(loader.context, target)
            posts = islice(profile.get_posts(), limit)

            for i, post in enumerate(posts, 1):
                print(f'[{i}/{limit}] {post.shortcode}')
                loader.download_post(post, target=target)
                save_caption(out / target / f'{post.date_utc:%Y-%m-%d}_{post.shortcode}', post)
                time.sleep(5)

        zip_file = make_zip(out)
        print('다운로드 완료')
        print(f'{zip_file.resolve()} 를 Codespace에서 Download 하세요.')

    except instaloader.exceptions.ConnectionException as e:
        print('Instagram 요청 제한(429) 발생')
        print('로그인 세션을 사용하거나 잠시 후 다시 시도하세요.')
        print(e)


if __name__ == '__main__':
    main()

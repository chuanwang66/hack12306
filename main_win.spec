# -*- mode: python -*-

block_cipher = None


a = Analysis(['hack12306.py'],
             pathex=['C:\\Python35\\Lib\\site-packages\\PyQt5', 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86', '.'],
             binaries=[
                ('chromedriver.exe', '')
             ],
             datas=[
                ('config_default.ini', ''),
                ('city_code.txt', ''),
                ('qiangpiao.txt', '')
             ],
             hiddenimports=[
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='qiangpiao',
          debug=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='qiangpiao')

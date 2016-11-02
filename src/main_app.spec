# -*- mode: python -*-

from glob import glob

block_cipher = None

gir = '/usr/share/gir-1.0'

a = Analysis(['main_app.py'],
             pathex=['/home/javierlopm/Documents/sistemaPermisosComputacion/src'],
             binaries=[('/usr/share/gir-1.0/*.gir','/usr/share/gir-1.0')
                      ,('/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/','gdk-pixbuf-query-loaders')
                      ],
             datas=[],
             hiddenimports=['selenium'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.datas += [("client_secret.json",'client_secret.json','DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main_app',
          debug=False,
          strip=False,
          upx=True,
          console=True )

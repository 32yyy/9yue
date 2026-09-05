#!/usr/bin/env python3
import re

FLUTTER_BUILD = ".github/workflows/flutter-build.yml"
FLUTTER_NIGHTLY = ".github/workflows/flutter-nightly.yml"

# ============================================================
# 修改 flutter-build.yml
# ============================================================
with open(FLUTTER_BUILD, "r") as f:
    content = f.read()

if 'CUSTOM_SUFFIX: "${{ secrets.CUSTOM_SUFFIX }}"' in content:
    print("✅ flutter-build.yml 已包含自定义配置，跳过")
else:
    # 1. 在 default: "nightly" 后面添加 secrets
    search_text = 'default: "nightly"'
    if search_text in content:
        indent = '    '
        secrets_block = f'''{indent}secrets:
{indent}  # ===== 新增的自定义 secrets =====
{indent}  RENDEZVOUS_SERVER:
{indent}    required: false
{indent}  RS_PUB_KEY:
{indent}    required: false
{indent}  API_SERVER:
{indent}    required: false
{indent}  DEFAULT_PASSWORD:
{indent}    required: false
{indent}  RELAY_SERVER:
{indent}    required: false
{indent}  CUSTOM_SUFFIX:
{indent}    required: false
{indent}  SOS_MODE:
{indent}    required: false
'''
        content = content.replace(search_text, search_text + '\n' + secrets_block)
        print("✅ 自定义 secrets 已添加")
    else:
        print("⚠️ 未找到 'default: \"nightly\"'")

    # 2. 在顶层 env 块末尾追加自定义变量
    if '# ===== 新增的自定义环境变量 =====' not in content:
        new_env_vars = '''  # ===== 新增的自定义环境变量 =====
  RS_PUB_KEY: "${{ secrets.RS_PUB_KEY }}"
  RENDEZVOUS_SERVER: "${{ secrets.RENDEZVOUS_SERVER }}"
  API_SERVER: "${{ secrets.API_SERVER }}"
  DEFAULT_PASSWORD: "${{ secrets.DEFAULT_PASSWORD }}"
  CUSTOM_SUFFIX: "${{ secrets.CUSTOM_SUFFIX }}"
  SOS_MODE: ${{ secrets.SOS_MODE }}'''
        
        content = re.sub(
            r'(env:\s*\n)((?:(?:[^\n]*\n)*?))(?=\n\s*jobs:)',
            r'\1\2' + new_env_vars + '\n',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        print("✅ 自定义 env 已添加")
    else:
        print("ℹ️ 自定义 env 已存在，跳过")

    # 3. 在文件名中添加 CUSTOM_SUFFIX
    # 使用 '' 代替 "" 避免 YAML 解析错误
    suffix_expr = r"${{ env.CUSTOM_SUFFIX != '' && format('-{0}', env.CUSTOM_SUFFIX) || '' }}"
    
    # 替换 .exe
    old_exe = 'mv ./target/release/rustdesk-portable-packer.exe ./SignOutput/rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.exe'
    new_exe = f'mv ./target/release/rustdesk-portable-packer.exe ./SignOutput/rustdesk-${{{{ env.VERSION }}}}-${{{{ matrix.job.arch }}}}{suffix_expr}.exe'
    
    if old_exe in content:
        content = content.replace(old_exe, new_exe)
        print("✅ .exe 后缀已添加")
    else:
        print("⚠️ 未找到 .exe 行")
    
    # 替换 .msi
    old_msi = 'rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.msi'
    new_msi = f'rustdesk-${{{{ env.VERSION }}}}-${{{{ matrix.job.arch }}}}{suffix_expr}.msi'
    
    if old_msi in content:
        content = content.replace(old_msi, new_msi)
        print("✅ .msi 后缀已添加")
    else:
        print("⚠️ 未找到 .msi 行")
    
    # 替换 -sciter.exe
    old_sciter = 'rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}-sciter.exe'
    new_sciter = f'rustdesk-${{{{ env.VERSION }}}}-${{{{ matrix.job.arch }}}}{suffix_expr}-sciter.exe'
    
    if old_sciter in content:
        content = content.replace(old_sciter, new_sciter)
        print("✅ -sciter.exe 后缀已添加")
    else:
        print("⚠️ 未找到 -sciter.exe 行")

    with open(FLUTTER_BUILD, "w") as f:
        f.write(content)
    print("✅ flutter-build.yml 自定义完成")

# ============================================================
# 修改 flutter-nightly.yml - 注释 schedule
# ============================================================
try:
    with open(FLUTTER_NIGHTLY, "r") as f:
        content = f.read()
    
    # 直接替换
    content = content.replace('  schedule:', '  # schedule:')
    content = content.replace('    - cron:', '    # - cron:')
    
    with open(FLUTTER_NIGHTLY, "w") as f:
        f.write(content)
    print("✅ flutter-nightly.yml 的 schedule 已注释")
    
except FileNotFoundError:
    print("⚠️ flutter-nightly.yml 不存在，跳过")

print("✅ 所有补丁完成")

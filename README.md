# Chai Sans / Chai Serif

基于思源黑体和思源宋体定制的字体，提供自动拆分系统所需的 PUA 字形显示。

## 源文件

字体源文件为 UFO（Unified Font Object）格式，位于 `sources/masters/`。UFO 格式的字体文件可以用所有主流字体编辑器来编辑。

## 构建

需要 Python 3。创建虚拟环境并安装依赖后，运行构建脚本：

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 build.py
```

输出文件写入 `dist/` 目录：

| 文件 | 格式 |
|------|------|
| `ChaiSans-Regular.otf` | OpenType CFF |
| `ChaiSans-Regular.woff` | WOFF（网页用） |
| `ChaiSans-Regular.woff2` | WOFF2（网页用，压缩率更高） |

## 构建 Chai Yuniversus

```
wget https://shurufa.app/fonts/yuniversus-chaipua.csv
```
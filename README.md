# 汉字自动拆分系统字体：Chai Sans / Chai Serif

基于思源黑体和思源宋体定制的字体，提供自动拆分系统所需的 PUA 字形显示。

## 安装依赖

请使用 Python 3 创建虚拟环境并安装依赖。

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 源文件

字体源文件为 UFO（Unified Font Object）格式，位于 `sources/masters/`。UFO 格式的字体文件可以用所有主流字体编辑器来编辑。

### 以使用 FontCreator 编辑为例：

1. 打开 FontCreator，选择 **File → Open**，将 `.ufo` 目录作为字体工程打开。
2. 在字形列表中找到需要编辑的字形，双击进入字形编辑器，完成轮廓修改。
3. 编辑完成后，选择 **File → Export Font As**，格式选择 **UFO**，覆盖保存到原 `.ufo` 目录（即 `sources/masters/` 下对应的目录）。

导出后，运行 `pre-commit.sh` 对 UFO 文件进行规范化格式化，并将变更暂存到 Git：

```bash
bash pre-commit.sh
```

该脚本会对 `sources/masters/` 下所有 `.ufo` 目录执行 `ufonormalizer`，统一缩进和元素顺序，使 diff 更易读。

## 构建

运行构建脚本：

```bash
python build.py
```

输出文件写入 `dist/` 目录：

| 文件 | 格式 |
|------|------|
| `ChaiSans-Regular.ttf` | OpenType TTF |
| `ChaiSans-Regular.otf` | OpenType CFF |
| `ChaiSans-Regular.woff` | WOFF（网页用） |
| `ChaiSans-Regular.woff2` | WOFF2（网页用，压缩率更高） |

## 构建 Chai Yuniversus

构建时，可以选择一同构建一个映射到宇浩 PUA 码位的字体。要如此做，请先下载宇浩 PUA 和 Chai PUA 的转换表：

```bash
wget https://shurufa.app/fonts/yuniversus-chaipua.csv
```

然后运行构建脚本即可。

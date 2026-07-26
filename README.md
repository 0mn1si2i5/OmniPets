# OmniPets

[English](README.en.md) · [中文说明](README.zh-CN.md)

OmniPets 是经过审查、可直接安装的宠物资产公开目录（public catalog），不是生成引擎，也不包含私有生产
项目。创作者使用开源 [OmniPet](https://github.com/0mn1si2i5/OmniPet) 完成生产、
QA、修复、打包、导出与验证。

## 当前示例：SuShi v1.0.1

![SuShi 预览](pets/sushi/preview.webp)

[SuShi](pets/sushi/) 是当前目录中的完整 sprite v2 示例。v1.0.1 已修复 hover/jumping
第五行主体偏小的问题，五帧主体尺度保持一致。安装时请同时使用该目录中的 `pet.json`
和 `spritesheet.webp`；不要复用旧版本图集。

## 安装宠物

浏览 [`catalog/index.json`](catalog/index.json)，选择 `pets/<pet-id>/`，把
`pet.json` 与 `spritesheet.webp` 一起安装到 Codex 宠物渲染器支持的目录。安装者
不需要模型凭据、checkpoint 或生产环境。

主分支只保留每只宠物的最新版；历史版本由不可变 tag 或托管 release 保存。复用前必须
阅读宠物目录中的 `LICENSE-ASSETS`，不同宠物的视觉资产许可和署名要求可能不同。

## 创作者发布流程

不要手工拼装未经验证的图集。在私有创作项目中用 OmniPet 完成打包与批准，再生成脱敏包：

```sh
omnipet release export <pet-id> --repo-root . --output release-work/<pet-id>
omnipet release verify release-work/<pet-id>
```

一次资产变更只能替换一个 `pets/<pet-id>/` 目录，并更新确定性生成的
`catalog/index.json`。公开 CI 会在没有 provider key 和私有仓凭据的环境中独立运行
`omnipet release verify`。

根目录 Apache-2.0 只覆盖目录代码与文档，不会重授权宠物美术资产；每只宠物的视觉资产
由其 `LICENSE-ASSETS` 单独约束。

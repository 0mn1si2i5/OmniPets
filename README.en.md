# OmniPets

[简体中文](README.md)

OmniPets is the public catalog of reviewed, installable pet assets. It is not
the generation engine and it does not contain private production projects.
Creators use the open-source [OmniPet](https://github.com/0mn1si2i5/OmniPet)
engine for production, QA, repair, packaging, export, and verification.

## Current example: SuShi v1.0.1

![SuShi preview](pets/sushi/preview.webp)

[SuShi](pets/sushi/) is the catalog's complete sprite v2 example. v1.0.1 fixes
the undersized body in the fifth hover/jumping row so all five frames keep a
consistent character scale. Install the `pet.json` and `spritesheet.webp` from
that directory together; do not reuse the superseded atlas.

## Install a pet

Browse [`catalog/index.json`](catalog/index.json), choose `pets/<pet-id>/`, and
install `pet.json` together with `spritesheet.webp` in the directory supported
by your Codex pet renderer. You do not need provider credentials, a checkpoint,
or a production environment.

The main branch keeps only the latest release of each pet. Historical versions
belong in immutable tags or hosted releases. Review `LICENSE-ASSETS` inside
each pet directory before reuse: visual asset licenses and attribution terms
may differ by pet.

## Publish as a creator

Do not manually assemble an unverified atlas submission. In a private creator
project, use OmniPet to build and approve the package, then create a sanitized
bundle:

```sh
omnipet release export <pet-id> --repo-root . --output release-work/<pet-id>
omnipet release verify release-work/<pet-id>
```

An asset change may replace exactly one `pets/<pet-id>/` directory and the
deterministically generated `catalog/index.json`. Public CI independently runs
`omnipet release verify` without provider keys or private-repository credentials.

The root Apache-2.0 license covers catalog code and documentation. It does not
relicense the pet artwork; each `LICENSE-ASSETS` controls its own visual assets.

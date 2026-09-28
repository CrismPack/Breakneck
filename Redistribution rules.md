# Redistribution rules

A few mods are only available on CurseForge or only on Modrinth, so the pack for the other platform can't download them and always bundles them instead. These are the ones whose licenses restrict bundling.

## Not allowed

- Voxy WorldGen (Modrinth only): [may only be downloaded from Modrinth](https://github.com/iSeeEthan/voxy_worldgen_v2/blob/main/LICENSE), so the CurseForge pack leaves it out (`curseforge_exclude` in `modpack-tool.yml`)

## Allowed with conditions

- voxy (Modrinth only): [link its Modrinth page and only use official versions](https://modrinth.com/mod/voxy)
- [Replanter Forked](https://github.com/Golinth/ReplanterForked) (Modrinth only, GPL-3.0), [ItemSwapper](https://github.com/tr7zw/ItemSwapper) (git builds are Modrinth only, LGPL-3.0) and [Framework](https://github.com/MrCrayfish/Framework) (CurseForge only, LGPL-2.1): link their source code where the pack is distributed

## Currently bundled

As of the last build (see `Export/bundled_links.md`):

- CurseForge pack:
  - ItemSwapper (LGPL-3.0)
  - Replanter Forked (GPL-3.0)
  - voxy (All Rights Reserved, allowed with conditions)
- Modrinth pack:
  - Controllable (MIT)
  - Framework (LGPL-2.1)

If a build bundles a mod that isn't on this list, that needs fixing: find out why it's bundled and whether its license allows it, then update this list.

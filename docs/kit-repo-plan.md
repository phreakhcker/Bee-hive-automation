# Kit repo plan

Tracking the split between this repo (open-source reference build) and a
separate private repo for the sellable kit version.

## Why two repos

This repo (`phreakhcker/Bee-hive-automation`) stays public and documents the
DIY reference build — salvaged 18650s, salvaged solar panel, hobby-grade BOM.
It is fine for a builder who wants to source parts themselves.

The kit repo will be **private** and will hold everything that only makes
sense for a shippable product:

- Productized BOM (Digikey/Mouser-stockable parts, 5-year lifecycle).
- LiFePO4 pack + certified charge controller (not salvaged Li-ion).
- Pre-certified radio modules where wireless is used (avoids FCC
  intentional-radiator cert cost).
- Assembly instructions written for a buyer, not a builder.
- Vendor pricing, margin sheets, fulfillment notes.
- Firmware forks that bundle only clean-IP models (see license audit in
  main repo README).
- Trademark / brand assets once a product name is chosen.

## Status

- Repo not yet created.
- Product name not yet chosen — see caveat below.
- Once created, seed from a curated subset of this repo (docs/, firmware/,
  pi/) and diverge from there.

## Naming caveat

GitHub renames redirect cleanly, but every existing clone's `origin` remote
still has to be updated by hand. Two options:

1. Pick the product name now and create the repo under that name.
2. Use a placeholder (`hive-kit-wip`, `kit-r0`) and rename before any public
   or commercial launch.

## Open questions

- Owner: personal account (`phreakhcker`) or a new org for the kit brand?
- Which parts of the current repo get copied vs. rewritten from scratch for
  a buyer audience?
- License for the kit repo's firmware — kit code can stay permissive (MIT)
  even in a private repo; the private/paid part is the hardware + assembled
  units, not the source.

## Related

- License audit that constrains what can ship: `README.md` → Acknowledgements.
- Dataset outreach that must resolve before the pollen model can ship in a
  kit: `docs/dataset-permissions.md`.

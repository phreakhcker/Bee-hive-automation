# Dataset permission outreach

Tracking commercial-use permission requests for third-party datasets we'd like to use in the pollen classifier.

Why this file exists: we plan to ship this project as a kit eventually. Several of the best public pollen datasets have no license file attached, which under default copyright law means we have no rights to use them beyond fair-use research. Rather than assume, we ask.

## Status

| Dataset | Contact | Sent | Reply | Outcome |
|---|---|---|---|---|
| PollenBee (HUST) | Prof. Le Thi Lan + Prof. Vu Hai (MICA / HUST ComVis) | — | — | pending |
| VnPollenBee (Nguyen et al. 2024) | same authors | — | — | pending |

Update this table when the email goes out and when replies arrive.

## Email template — HUST (PollenBee / VnPollenBee)

**Recipients** (verified 2026-07-26 against MICA staff pages + ComVis-HUST team page):

- **To:** `Thi-Lan.Le@mica.edu.vn`, `hai.vu@mica.edu.vn`
- **Cc:** `lanltbk@gmail.com`, `haicuhn@gmail.com`

Prof. Le Thi Lan is the head of the ComVis group and the primary corresponding contact — listed first for that reason. The `@mica.edu.vn` addresses are institutional (medium confidence — the MICA site hasn't been updated since ~2021 but mailboxes likely still forward); the gmail addresses are published on the current ComVis-HUST GitHub team page and are medium-high confidence. Sending to both per person maximises delivery.

If no reply in ~10 days: fallback is the contact link on https://comvis-hust.github.io/ or ResearchGate direct message to Prof. Le.

**Subject:** Request for commercial-use permission — PollenBee / VnPollenBee dataset

---

Dear Prof. Le and Prof. Vu,

I am building an open-hardware beehive monitoring system that includes camera-based detection of pollen loads on returning honeybees. Through your ComVis HUST group page and your 2024 paper on pollen-bearing bee detection, I found the PollenBee and VnPollenBee datasets, which look ideal for the classifier I need to train.

I did not find a license file bundled with either dataset, so I would like to ask directly before using them:

1. Under what terms are the PollenBee and VnPollenBee datasets released for external researchers to use?
2. My longer-term goal is to sell the monitoring system as a kit to hobbyist beekeepers. Would training a pollen-detection model on your datasets and distributing the resulting model weights inside a commercial product be permitted, either freely, under attribution, or under a licensing arrangement you would prefer?

I will of course cite both datasets and your related publications in all project documentation, and I am happy to link back to your group's page from the kit's software repository.

The project is open-source and lives at https://github.com/phreakhcker/Bee-hive-automation — the pollen detection component is described in the README.

Thank you for making the datasets available in the first place, and for any guidance you can offer on their use.

Kind regards,

Jeremy Franklin
maker86industries@gmail.com

---

## Notes for future outreach

- If PollenBee/VnPollenBee come back as research-only, the fallback is to collect our own dataset from the prototype hive once cameras are installed. That's the only fully clean-IP path for a shipping model.
- If we later want to use the Mendeley bee-direction dataset (8gb9r2yhfc) for anything more than internal benchmarking, we'd need a separate ND waiver from the authors — CC-BY-NC-ND is otherwise fatal.
- Do NOT email authors from a personal address if we later want the response to have any commercial weight — use a project domain email once we have one.

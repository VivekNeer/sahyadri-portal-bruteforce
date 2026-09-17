<h1 align="center">Sahyadri Portal — Scripts</h1>

<p align="center">
  <b>Python scripts for diagnosing and testing a campus captive-portal login.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/domain-Captive%20Portal-2b6cb0?style=flat-square" alt="Captive Portal">
  <img src="https://img.shields.io/badge/use-Educational-important?style=flat-square" alt="Educational">
</p>

---

## Overview

A small set of Python scripts written while exploring how the Sahyadri campus internet **captive portal** works. The portal speaks a simple XML login/logout protocol over HTTP, and these scripts interact with it programmatically.

## Contents

| File | What it does |
|---|---|
| `portal_diagnose.py` | Network diagnostic helper — checks connectivity/reachability to the portal host and writes a `portal_diag.log` summary |
| `brute_force.py` | Iterates candidate credential ranges (`ranges.csv`) against the portal's `login.xml` endpoint and records which resolve to valid users |
| `httpclient.js` / `login_page.html` | Captured portal login page and a JS client reference |
| `ranges.csv`, `valid_users.txt` | Input/output data files |

## ⚠️ Responsible Use

This repository is a **personal learning exercise** in HTTP, captive-portal protocols, and scripting. It is intended only for use on networks and accounts you own or are explicitly authorised to test. Probing or attempting to access systems or accounts without permission is against most acceptable-use policies and may be illegal. Use it responsibly and at your own risk.

## Requirements

- Python 3
- Network access to the target portal host

```bash
python3 portal_diagnose.py
```

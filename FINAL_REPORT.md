# Shipwright — Final Delivery Report

## Project

**Shipwright** هو أداة CLI محلية لتحليل جاهزية مستودعات البرمجيات للإصدار. المشكلة التي يحلها هي تشتت إشارات الجودة بين README والاختبارات وCI والترخيص والتغليف والأمان؛ أما القيمة فهي تحويل هذه الإشارات إلى verdict واحد مدعوم بمسارات evidence، مع JSON وMarkdown وSARIF وpolicy-as-code.

Repository: https://github.com/Alqudimi/shipwright  
Release: https://github.com/Alqudimi/shipwright/releases/tag/v0.1.0  
Preview checkpoint: `manus-webdev://a8ad98fb`

## Why this project

أظهر تدقيق الحساب وجود قوة واضحة في Python وAI/security tooling وMCP وreproducibility، مع تكرار حديث في agent/MCP tools. لذلك تم استبعاد MCP scanner وpolicy gateway وagent replay جديدة. البحث قارن Shipwright مع OpenLineage وMarquez وDVC وMLflow ومنصات AI observability وأدوات MCP security؛ وخلص إلى أن الفجوة الأعلى قيمة للحساب هي منتج flagship يركز على release engineering وmaintainer experience وopen-source readiness، لا أداة agent أخرى.

## Engineering

المعمارية مقسمة إلى نماذج domain immutable في `shipwright_core/models.py`، وكاشفات deterministic في `detectors.py`، ومحرك orchestration وسياسات في `engine.py` و`policy.py`، ومحولات إخراج في `renderers.py`، وواجهة CLI في `cli.py`. النواة لا تنفذ كود المستودع المفحوص، ولا تشغل shell commands، ولا ترسل source عبر الشبكة، وتتعامل مع repository كـ untrusted input.

الـ stack هو Python 3.11+ وstdlib/TOML وHatchling وpytest وRuff وMypy، مع React 19 وTypeScript/Tailwind في واجهة التقرير البصرية. لم تُضف قاعدة بيانات أو خدمة خارجية لأن المنتج local-first، deterministic، وقابل للعمل offline. أضيفت سياسة `shipwright.toml` لتحديد minimum score وrequired checks. النواة قابلة للتوسع بإضافة detectors وrenderers وprovider adapters اختيارية دون تغيير عقد JSON.

## Implemented product

التنفيذ الحالي يفحص structure وdocumentation وtests وGitHub Actions وlicense وpackage metadata وsecret hygiene المحافظ. أوامر الاستخدام هي:

```bash
python -m pip install shipwright-readiness==0.1.0
shipwright inspect .
shipwright inspect . --format json --output report.json
shipwright inspect . --format sarif --output shipwright.sarif
shipwright gate .
```

واجهة Shipwright تعرض Evidence Ledger غير متماثل بهوية warm-paper وink وShipwright Copper، مع readiness verdict، score، filters، selected evidence drawer، responsive layout، favicon، وgenerated visual identity asset.

## Quality evidence

| Check | Result |
|---|---|
| Unit/integration tests | 6 passed |
| Coverage | 92.77% measured locally; threshold 85% |
| Ruff | Passed |
| Mypy strict | Passed |
| Python package build | Passed; sdist and wheel generated |
| Frontend build | Passed via `pnpm build` |
| CLI inspect | Passed; JSON report generated |
| CLI gate | Passed on the final repository |
| Clean clone | Passed from GitHub tag `v0.1.0`; install, tests, and gate passed |
| GitHub Actions | Passed on Python 3.11 and 3.12 |
| Security posture | No real secrets committed; conservative scan; no target-code execution |

The frontend build emitted a non-blocking bundle-size warning and a runtime-resolved `/manus-storage` asset notice. GitHub Actions emitted a non-blocking Node.js 20 deprecation annotation from upstream action versions; all quality jobs succeeded.

## GitHub

The repository is public at `Alqudimi/shipwright`, default branch `main`, with five commits and release `v0.1.0`. The actual push succeeded after using a separate `github` remote because the managed project reserves `origin` for internal storage. GitHub Actions run: https://github.com/Alqudimi/shipwright/actions/runs/31961586725 and conclusion was `success`.

Commits use meaningful messages: `feat(core): add evidence-backed readiness engine`, `docs(maintainer): add open source project foundation`, `feat(ui): build evidence ledger report viewer`, and `chore: ignore generated Python artifacts`.

## Documentation

The repository includes README, architecture documentation, policy example, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, LICENSE, GitHub Actions, and issue-ready project structure. The README explains the problem, contract, usage, architecture, security model, development commands, and roadmap without depending on a hosted service.

## Final assessment

كـ Senior Engineer، المشروع يثبت separation of concerns وtyped domain وpolicy boundaries واختبارات قابلة لإعادة التشغيل. كـ Open Source Maintainer، يحتوي على MIT license وcontribution/security guidance وCI وrelease. كـ Recruiter، يعرض منتجًا واضحًا يجمع CLI وsecurity وtesting وpackaging وfrontend evidence viewer. كـ GitHub User، يمكن clone/install/run المشروع من tag نظيف، والـ README يشرح أول مسار تشغيل خلال دقائق.

## Known limitations and next steps

المشروع v0.1.0 ولا يدّعي أنه بديل كامل لـ OpenSSF Scorecard أو secret scanners المتخصصة. الخطوة الطبيعية التالية هي إضافة detectors اختيارية لـ changelog وSPDX وdependency metadata وreproducible commands، ثم إضافة SARIF upload action وPR annotations بصلاحيات read-only افتراضيًا. كما ينبغي خفض حجم bundle عبر code splitting إذا تحولت الواجهة إلى تطبيق أكبر.

## References

[1]: https://openlineage.io/ "OpenLineage official project"
[2]: https://marquezproject.ai/ "Marquez official project"
[3]: https://dvc.org/ "DVC official project"
[4]: https://mlflow.org/docs/latest/ml/tracking/ "MLflow Tracking documentation"
[5]: https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/ "AI agent observability comparison"
[6]: https://github.com/clay-good/agent-replay "agent-replay repository"
[7]: https://nordicapis.com/10-tools-for-securing-mcp-servers/ "MCP security tools comparison"


## Hardening addendum — v0.2.0

تمت مراجعة الحالة المنشورة وإضافة hardening عالي الأثر دون تغيير فلسفة local-first. أضيف `Dockerfile` يعمل بمستخدم غير root، و`.dockerignore`، وSecurity workflow مجدول وعلى pull requests باستخدام `pip-audit` و`zizmor --offline`. أُثبتت Actions على commit SHAs مع `persist-credentials: false`، وأصبح SARIF يحمل rule metadata وremediation help و`%SRCROOT%` locations المتوافقة مع عرض GitHub Code Scanning.

أضيفت قوالب Pull Request وbug وfeature، ووثيقة `docs/improvement-audit.md` التي تشرح لماذا يتكامل Shipwright مع OpenSSF Scorecard وzizmor بدل إعادة تنفيذ محركاتهما. ارتفعت التغطية المقاسة إلى **94.09%** مع 6 اختبارات ناجحة، ونجحت Ruff وstrict Mypy وبناء الحزمة و`pip-audit` وzizmor offline. نجحت GitHub Actions للـ CI والـ Security على commit `ab52c5c`، وتم نشر الإصدار [v0.2.0](https://github.com/Alqudimi/shipwright/releases/tag/v0.2.0).

اختبار Docker الفعلي تعذر فقط لأن sandbox لا يحتوي على Docker أو Podman أو Buildah؛ تم التحقق من Dockerfile و`.dockerignore` ثابتًا، ووُثّق هذا القيد في release notes بدل الادعاء بتشغيل لم يحدث.


## v0.3.x provenance verification addendum

أضيف في هذه الدورة مسار release provenance حقيقي إلى `.github/workflows/release.yml`. عند إنشاء v0.3.0 ظهر فشل فعلي في خطوة attestation بسبب غياب `predicate-type`. بعد إضافة SLSA predicate ظهر فشل ثانٍ لأن الاستخدام المباشر لـ `actions/attest` يتطلب `predicate` أو `predicate-path`. تم تشخيص ذلك من سجل GitHub، ثم استُبدل الاستخدام بالـ wrapper الرسمي المثبت `actions/attest-build-provenance`، ووُثّقت واجهة القرار في `docs/release.md`.

تم إنشاء v0.3.2 من commit `ed4f816` بعد نجاح CI وSecurity. تشغيل Release رقم `32262808931` نجح بالكامل: بناء الحزمة، رفع artifacts، وإنشاء attestation provenance. هذا هو أول تحقق فعلي مكتمل لمسار provenance، وليس مجرد فحص YAML أو ادعاء غير منفذ. كما نجحت تشغيلات CI وSecurity على نفس commit، ونجحت محليًا الاختبارات الستة بتغطية 94.09%، Ruff، strict Mypy، build، pip-audit، وzizmor offline.

القيود المتبقية: لم أختبر `gh attestation verify` على ملف wheel محليًا لأن artifact الناتج يعيش داخل GitHub Actions ولم يتم تنزيله إلى sandbox؛ لكن خطوة attestation نفسها نجحت في GitHub Actions. كما أن Docker runtime غير متوفر في البيئة، لذلك لا يوجد ادعاء بتشغيل container فعلي.


## v0.3.3 release-assets addendum

كشفت المراجعة الجديدة فجوة عملية: provenance كان ناجحًا، لكن artifacts لم تكن تُرفق بصفحة GitHub Release. أضيفت خطوة `gh release upload` مع `contents: write` مقيّدة إلى workflow release، ثم كشف `zizmor` template injection عالي الثقة بسبب إدخال GitHub context داخل `run`. تم إصلاحه بتمرير `github.ref_name` و`github.repository` عبر environment variables؛ بعد الإصلاح نجحت جميع بوابات الجودة محليًا، ونجح CI وSecurity على commit `d38283c` دون findings.

تم نشر v0.3.3 وتشغيل Release رقم `32378101520` بنجاح كامل: build، upload artifact، attestation، ثم attach assets إلى GitHub Release. تم تنزيل الملفين من GitHub فعليًا في sandbox للتحقق المستقل:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `shipwright_readiness-0.1.0-py3-none-any.whl` | 14,385 bytes | `4134fd50090b482dff26287633a8ba43d666177bf9e62e5056db32d618bdb9a4` |
| `shipwright_readiness-0.1.0.tar.gz` | 158,047 bytes | `c051cfdecbc1d590cce21618a18e318a64f7cb0a8e1beae2f1390586175d24a2` |

أصبح مسار الإصدار الآن قابلًا للاستخدام من منظور المستهلك: تنزيل مباشر من صفحة Release، provenance موقّع، وإمكانية التحقق عبر `gh attestation verify`. لم أعدّل أي مستودع قائم آخر، ولم تُستخدم أسرار طويلة العمر.

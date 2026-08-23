# 웹소설 서가

한국어·영어 웹소설을 한 저장소에서 기획하고 검증하며 정적 사이트, 합본 문서, EPUB으로 출판하는 표준 라이브러리 전용 파이프라인입니다. 출간작·기획작·은퇴작을 같은 작품 구조 안에서 명시적으로 분리합니다.

- **출간:** 무림철폐론자 — 상처를 닫는 대장장이
- **기획:** 칠대고수가 죽고 점소이만 회귀했다 *(가제)*
- **은퇴:** 회귀자 일곱이 죽고 점소이만 남았다 — 원고·번역·삽화와 출시 기록은 보존하되 새 빌드에서는 제외

## 구조

```text
AGENTS.md                            # 작업 시작 전에 읽는 운영 지침(CLAUDE.md가 이 파일을 불러옴)
catalog.json                         # published / planning / retired 수명주기와 legacy alias
stories/<slug>/
  story.json                         # 수명주기와 한국어 정본·출판 메타데이터
  locales/en.json                    # 선택적 영어판 메타데이터
  manuscript/                        # 바이블, 개요, 오버레이, 연속성 장부, 정본, 번역, 편집 개요
  reference/                         # 장기 세계관 자료(정본 아님)
  editorial/                         # 그 작품의 리뷰와 감사 기록
  assets/cover.svg                   # 필수 표지
  assets/cover-en.svg                # 선택적 영어 표지
  assets/scenes/                     # 선택적 승인 삽화
site/                                # 모든 작품이 공유하는 CSS, JS, 폰트, favicon
scripts/novel.py                     # catalog validate / stats / build / promote-check
scripts/release_check.py             # 실패 시 중단하는 통합 출시 게이트(CI가 실행)
tests/                               # stdlib unittest
docs/authoring-pipeline.md            # 기획부터 교정·삽화·출시까지 재사용 절차
docs/fiction-craft-standard.md       # 장르 공통 집필·검토 기준
dist/                                # 생성 결과(Git 제외)
```

`catalog.json`의 `stories`는 출간작, `projects`는 기획·집필 중인 작품, `retired_stories`는 철회됐지만 보존하는 작품입니다. 세 배열의 slug는 서로 중복될 수 없고 `stories/<slug>/story.json`의 `slug` 및 `status`와 정확히 맞아야 합니다. 빌드와 공개 서가는 `stories`만 처리합니다. 기획작은 불완전 원고 때문에 빌드를 깨지 않으며, 은퇴작은 삭제하지 않고 역사와 재사용 근거를 남깁니다. 어떤 수명주기에도 등록되지 않은 `story.json` 폴더는 오류입니다. `legacy_alias_story`는 반드시 출간작이어야 합니다.

## 실행

Python 3 외 의존성은 없습니다.

```bash
python3 -m unittest -v
python3 scripts/novel.py validate
python3 scripts/novel.py stats
python3 scripts/novel.py build
python3 scripts/novel.py promote-check --story <slug>   # 출간 승격을 막는 항목만 보고(변경 없음)
python3 scripts/release_check.py          # 테스트·빌드·링크·EPUB 일괄 게이트
python3 scripts/release_check.py --docker # 컨테이너까지 포함한 최종 게이트
```

출간작은 `manuscript/`에 `story-bible.md`, `outline.md`, `craft-overlay.md`, `continuity-ledger.md`를 갖춰야 하고, `illustrations.json`이 있으면 `visual-bible.md`도 필요합니다. 의도적으로 비워 둔 항목은 `story.json`의 `artifact_exceptions`에 사유와 함께 기록해야 하며, 사유가 비어 있거나 파일이 실제로 존재하면 검증이 실패합니다. 기획작은 이 검사에서 면제되고 `promote-check`로 승격 전에 확인합니다.

`validate`와 `stats`는 기본적으로 모든 **출간작**을 처리하며 `--story <slug>`로 한 출간작만 선택할 수 있습니다. `build`는 출간작 전체를 먼저 검증한 다음 공개 카탈로그를 임시 디렉터리에 만들고 `dist/`를 교체합니다. `projects`와 `retired_stories`는 수명주기·경로·메타데이터만 검증하고 공개 결과에는 넣지 않습니다.

## 공개 경로

```text
/                                           # 작품 카탈로그
/stories/<slug>/                            # 한국어 작품 홈
/stories/<slug>/chapters/01.html            # 한국어 회차
/stories/<slug>/en/                         # 영어 작품 홈(존재할 때)
/stories/<slug>/en/chapters/01.html         # 영어 회차
/stories/<slug>/<slug>.{md,html,txt,epub}   # 한국어 합본
/stories/<slug>/en/<slug>.{md,html,txt,epub}# 영어 합본
```

첫 번째 카탈로그 작품은 이전 배포 링크를 계속 제공합니다. 현재 `murim-abolitionist`에 대해 `/chapters/*.html`, `/en/`, `/en/chapters/*.html`, `/murim-abolitionist.{md,html,txt,epub}`가 유지되며 HTML에는 canonical 작품 URL과 절대 탐색·언어·자산 링크가 들어갑니다.

읽기 진행률, 마지막 회차, 테마, 글자 크기는 `webnovel:<slug>:...` localStorage 키로 작품별 격리됩니다. 집중 읽기는 `◎` 버튼으로 각 페이지에서 명시적으로 켜며, 현재 문단만 선명하게 유지하고 탭·Space·J/K·↑↓로 약 0.2–0.4초 안에 다음 문단으로 이동합니다. 새 페이지에서 갑자기 본문이 흐려지지 않도록 집중 모드는 저장하지 않습니다. `Esc`로 즉시 끝나고 운영체제의 reduced-motion 설정에서는 애니메이션을 생략합니다. 기존 `murim-*` 키는 `murim-abolitionist`에서 새 키가 비어 있을 때 한 번 호환 복사됩니다. 로그인이나 서버 저장소는 없습니다.

## 새 작품 시작과 출간

1. `stories/<slug>/story.json`을 `status: planning`으로 만들고 slug를 `catalog.json`의 `projects`에 넣습니다.
2. `docs/authoring-pipeline.md`에 따라 production status, concept decision, story bible, architecture, outline, craft overlay, continuity ledger를 먼저 잠급니다.
3. 명시적 집필 승인 뒤에만 `manuscript/chapters/`를 만들고 한국어 정본을 작성합니다.
4. 번역·리뷰·표지·삽화·출시 게이트를 모두 통과하면 `status`를 `published`로 바꾸고 slug를 `projects`에서 `stories`의 원하는 공개 순서로 옮깁니다.
5. 대체되거나 철회된 작품은 삭제하지 말고 `status: retired`와 교체 사유·백업 브랜치를 기록한 뒤 `retired_stories`로 옮깁니다.
6. 모든 수명주기 변경 후 테스트, `validate`, `stats`, `build`를 실행합니다.

작업을 시작하기 전에 [`AGENTS.md`](AGENTS.md)를 읽습니다. 의도적으로 미뤄 둔 작업은 [`docs/planned-work.md`](docs/planned-work.md)에 사유와 착수 조건까지 기록합니다. 전체 제작은 [`docs/authoring-pipeline.md`](docs/authoring-pipeline.md), [`docs/fiction-craft-standard.md`](docs/fiction-craft-standard.md), [`docs/web-novel-production-playbook.md`](docs/web-novel-production-playbook.md)를 따릅니다. `docs/templates/`에는 작품 진행표, 연속성 장부, 비주얼 바이블 템플릿이 있습니다. 이전 회귀작의 보상 연구와 선택 기록은 역사 자료로 남지만 새 기획의 정본은 `stories/seven-masters-returned/` 안에 있습니다. 기계 검사는 문학적 품질을 판정하지 않고 누락, 번호, 길이, 오염, 반복 같은 값싼 오류를 막습니다.

삽화는 기본 절차가 아니라 명시적으로 요청했을 때만 진행하는 선택 트랙입니다. 삽화가 없어도 작품은 모든 게이트를 통과하고 정상적으로 출시됩니다. 삽화를 넣을 때도 정본 Markdown에 공급자 문법을 넣지 않습니다. `manuscript/illustrations.json`에서 언어별 문단 위치, 로컬 `assets/scenes/` 파일, 대체 텍스트와 생성 provenance를 선언합니다. 빌더는 경로 탈출, 누락 파일, 언어별 배치, provenance를 검증하고 승인된 이미지만 독서 페이지에 삽입합니다.

## Dokploy / Docker

Dokploy에서 `Dockerfile` 애플리케이션으로 연결합니다.

- 컨테이너 포트: `8080`
- 헬스체크: `GET /healthz` → `200 ok`
- 환경 변수·데이터베이스·볼륨: 없음

```bash
docker build -t webnovel-catalog:local .
docker run --rm -p 8080:8080 webnovel-catalog:local
curl -f http://127.0.0.1:8080/healthz
```

빌더는 테스트, 전체 카탈로그 검증, 전체 빌드를 통과한 정적 결과물만 non-root Nginx 이미지로 복사합니다.

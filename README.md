# 웹소설 서가

한국어·영어 웹소설을 한 저장소에서 검증하고 정적 사이트, 합본 문서, EPUB으로 출판하는 표준 라이브러리 전용 파이프라인입니다. 서로 다른 독서 경험을 의도적으로 시험하는 두 작품을 담습니다.

- **무림철폐론자 — 상처를 닫는 대장장이:** 제도, 책임, 연대에 무게를 둔 무협.
- **회귀자 일곱이 죽고 점소이만 남았다:** 예측, 역전, 획득, 성장 보상을 최대한 자주 전달하는 도파민 우선 무협.

## 구조

```text
catalog.json                         # 공개 순서와 고정 legacy alias 작품
stories/<slug>/
  story.json                         # 한국어 정본·출판 메타데이터
  locales/en.json                    # 선택적 영어판 메타데이터
  manuscript/                        # 정본, 번역, 편집 개요
  assets/cover.svg                   # 필수 표지
  assets/cover-en.svg                # 선택적 영어 표지
site/                                # 모든 작품이 공유하는 CSS, JS, 폰트, favicon
scripts/novel.py                     # catalog validate / stats / build
tests/                               # stdlib unittest
docs/fiction-craft-standard.md       # 장르 공통 집필·검토 기준
dist/                                # 생성 결과(Git 제외)
```

`catalog.json`의 slug는 중복될 수 없고 `stories/<slug>/story.json`의 `slug`와 정확히 같아야 합니다. `legacy_alias_story`는 공개 순서와 독립적으로 이전 주소를 계속 담당할 작품을 고정합니다. `story.json`이 있는 미등록 작품 폴더도 검증 오류로 처리해 완성 원고가 빌드에서 조용히 빠지지 않게 합니다. 작품별 장르, 인용문, 소개, 완독 문구는 템플릿이 아니라 각 판본 메타데이터에 둡니다. `research/`는 설계 근거와 한계를 보존하며 원고 정본과 분리합니다.

## 실행

Python 3 외 의존성은 없습니다.

```bash
python3 -m unittest -v
python3 scripts/novel.py validate
python3 scripts/novel.py stats
python3 scripts/novel.py build
```

`validate`와 `stats`는 기본적으로 카탈로그 전체를 처리하며 `--story <slug>`로 한 작품만 선택할 수 있습니다. `build`는 항상 모든 작품을 먼저 검증한 다음 전체 카탈로그를 임시 디렉터리에 만들고 `dist/`를 교체합니다. 따라서 뒤쪽 작품의 검증 실패가 기존 배포본을 부분적으로 지우지 않습니다.

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

읽기 진행률, 마지막 회차, 테마, 글자 크기는 `webnovel:<slug>:...` localStorage 키로 작품별 격리됩니다. 기존 `murim-*` 키는 `murim-abolitionist`에서 새 키가 비어 있을 때 한 번 호환 복사됩니다. 로그인이나 서버 저장소는 없습니다.

## 새 작품 추가

1. `stories/<slug>/` 아래에 `story.json`, `manuscript/chapters/`, `manuscript/reviewer-notes/ko/`, `assets/cover.svg`를 만듭니다.
2. 번역이 있으면 `locales/en.json`, `manuscript/translations/en/chapters/`, `manuscript/reviewer-notes/en/`와 필요 시 `assets/cover-en.svg`를 추가합니다.
3. `catalog.json`의 원하는 공개 순서에 slug를 추가합니다.
4. `validate`, `stats`, 테스트, `build`를 실행합니다.

원고 집필·편집은 [`docs/fiction-craft-standard.md`](docs/fiction-craft-standard.md)와 [`docs/web-novel-production-playbook.md`](docs/web-novel-production-playbook.md)를 따릅니다. 두 번째 작품의 보상 설계와 근거 경계는 [`research/dopamine-serial-design.md`](research/dopamine-serial-design.md)에 기록했습니다. 기계 검사는 문학적 품질을 판정하지 않고 누락, 번호, 길이, 오염, 반복 같은 값싼 오류를 막습니다.

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

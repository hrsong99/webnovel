# 무림철폐론자 — 상처를 닫는 대장장이

고수들의 결투로 가족과 마을을 잃은 대장장이 진철이, 복수가 아니라 무림이라는 치외법권 자체를 끝내려는 한국어 무협 웹소설 프로젝트입니다.

이 저장소는 **좋은 원고를 만드는 일**과 **원고를 기계적으로 검증·배포하는 일**을 분리합니다. 모델이나 제공자에 종속된 자동 생성기를 두지 않습니다. 사람 또는 어떤 집필 에이전트든 동일한 작품 바이블과 회차 구성을 읽고 원고를 쓸 수 있고, 표준 라이브러리만 사용하는 로컬 도구가 결과를 검증하고 전자책으로 묶습니다.

## 현재 결과물

- 제1권 미니 아크 6화, 한국어 정본과 완역 영어판
- 회차마다 접을 수 있는 한·영 편집자용 플롯 개요
- 순수 원고 Markdown과 번역 용어·문체 계약
- 빌드 결과: 한·영 작품 홈, 회차별 리더, 합본 HTML, Markdown, TXT, EPUB 3
- 언어 전환, 읽기 진행률, 테마·글자 크기 로컬 저장
- 연속성·문체 계약과 회차별 구성
- 길이, 누락, 번역 완결성, 기획 메모 혼입, 자리표시자, 과도한 문장 반복을 검사하는 CLI
- 임시 픽스처 기반 자동 테스트

## 구조

```text
story.json                    # 한국어 제목, 언어, 회차 수, 길이 기준
locales/en.json               # 영어판 출판 메타데이터와 단어 수 기준
manuscript/
  story-bible.md              # 정본 설정·인물·문체·성장 제약
  outline.md                  # 제1권 인과관계와 회차별 독자 보상
  chapters/                   # 한국어 정본 본문
  translations/en/            # 영어판 본문과 번역 계약
  reviewer-notes/{ko,en}/     # 접을 수 있는 편집자용 플롯 개요
docs/fiction-craft-standard.md       # 모든 장르에 쓰는 집필·검토·개작 기준
docs/web-novel-production-playbook.md # 후속 권을 위한 집필·편집·배포 교훈
research/fiction-craft/             # 위 기준의 조사 근거와 출처
research/source/              # 이전 시도, 원본 대화, 세계관 자료(참고용)
scripts/novel.py              # validate / stats / build
site/                         # 공개 리더 CSS·JavaScript·표지 원본
Dockerfile                    # Dokploy용 멀티스테이지 프로덕션 이미지
compose.yaml                  # 선택 가능한 Dokploy Compose 진입점
deploy/nginx.conf             # non-root Nginx와 헬스체크
tests/                        # stdlib unittest
dist/                         # 생성된 웹사이트·전자책; Git 제외
editorial/                    # 교정 기록과 최종 편집 보고서
```

`research/source/`는 설계의 역사이며 정본이 아닙니다. 충돌할 경우 `story.json`과 `manuscript/story-bible.md`가 우선합니다.

## 실행

Python 3 외 의존성은 없습니다.

```bash
python3 -m unittest -v
python3 scripts/novel.py validate
python3 scripts/novel.py stats
python3 scripts/novel.py build
```

빌드가 성공하면 다음 파일이 생깁니다.

```text
dist/index.html                         # 한국어 작품 홈
dist/chapters/01.html ... 06.html       # 한국어 회차별 리더
dist/en/index.html                      # English edition home
dist/en/chapters/01.html ... 06.html    # English chapter reader
dist/assets/cover.svg                   # 한국어 표지
dist/assets/cover-en.svg                # 영어 표지
dist/murim-abolitionist.epub            # 한국어 EPUB
dist/en/murim-abolitionist.epub         # English EPUB
dist/{,en/}murim-abolitionist.{html,txt,md}
```

공개 리더에는 로그인이나 서버 저장소가 없습니다. 읽은 회차, 테마, 글자 크기는 해당 브라우저의 `localStorage`에만 보관됩니다.

## Dokploy 배포

가장 단순한 방법은 Dokploy에서 이 GitHub 저장소의 `main` 브랜치를 **Dockerfile** 애플리케이션으로 연결하는 것입니다.

- Dockerfile 경로: `Dockerfile`
- 컨테이너 포트: `8080`
- 헬스체크: `GET /healthz` → `200 ok`
- 환경 변수·데이터베이스·볼륨: 필요 없음
- 도메인 라우팅: Dokploy에서 컨테이너 포트 `8080`으로 연결

Compose 애플리케이션을 선호하면 저장소 루트의 `compose.yaml`을 사용하고 `web` 서비스의 포트 `8080`을 라우팅합니다. 두 방식 모두 빌드 단계에서 테스트, 원고 검증, 사이트 생성을 실행한 뒤 non-root Nginx로 정적 결과물만 제공합니다.

로컬 컨테이너 확인:

```bash
docker build -t murim-abolitionist:local .
docker run --rm -p 8080:8080 murim-abolitionist:local
curl -f http://127.0.0.1:8080/healthz
```

`main`에 원고나 사이트 자산을 푸시하면 Dokploy의 자동 배포가 새 이미지를 빌드하며, 새 회차와 목차·전자책이 함께 공개됩니다.

## 단순하지만 견고한 집필 순서

1. **계약 고정:** 작품 바이블에서 독자 약속, 힘의 한계, 시점, 금지할 지름길을 먼저 고정한다.
2. **회차 설계:** 각 화에 되돌릴 수 없는 선택, 구체적인 보상, 다음 행동을 촉발하는 끝을 둔다.
3. **순수 원고 작성:** `manuscript/chapters/`에는 본문만 둔다. 계획과 작가 메모를 복사하지 않는다.
4. **기계 검증:** `validate`로 번호·길이·오염·반복을 잡는다.
5. **세 번의 사람 검토:** 인과와 긴장 → 인물·연속성 → 한국어 문장과 리듬 순으로 교정한다.
6. **다시 검증하고 빌드:** 테스트, 검증, 통계, EPUB 구조 확인 뒤 배포본을 만든다.

기계 검사는 문학적 품질을 판정하지 않습니다. 검사가 맡는 것은 누락과 반복 같은 값싼 실수를 막는 일이며, 장면의 감정·인물의 선택·문장의 생동감은 별도 편집 과정에서 판단합니다.

새 작품이나 개작을 시작할 때는 장르 공통 기준인 [`docs/fiction-craft-standard.md`](docs/fiction-craft-standard.md)를 먼저 읽고, 이 저장소의 구체적인 제작 절차는 [`docs/web-novel-production-playbook.md`](docs/web-novel-production-playbook.md)를 따릅니다. 기준의 조사 근거는 [`research/fiction-craft/fundamentals.md`](research/fiction-craft/fundamentals.md), 독서 화면의 근거와 시각 원칙은 [`docs/reader-design-notes.md`](docs/reader-design-notes.md)에 남겨 두었습니다.

## 설계상의 핵심 선택

- 기존의 수동 YAML 템플릿 다섯 개는 실행되지 않았고 계획을 본문에 중복시켰습니다. 원본은 연구 자료로 보존하되 현재 워크플로에서는 사용하지 않습니다.
- 거대한 프롬프트 하나로 전권을 생성하지 않습니다. 짧은 정본 계약과 회차 구성으로 컨텍스트를 제한합니다.
- LLM API를 코드에 박지 않습니다. 품질은 제공자 선택보다 정본 관리, 독립 검토, 반복 수정에 더 크게 좌우되며, 결정적 빌드와 재현성도 유지됩니다.
- Git이 변경 이력을 제공하므로 각 회차 안의 변경 로그와 발췌문 복제본을 제거했습니다.

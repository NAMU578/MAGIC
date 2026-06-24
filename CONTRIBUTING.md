---
title: 홈페이지 수정 방법
---

이 홈페이지는 **GitHub에 있는 Markdown(.md) 파일을 수정하면 자동으로 갱신**됩니다. 코딩이나 HTML 지식은 필요 없습니다. 글쓰기처럼 내용만 고치면 됩니다.

## 가장 쉬운 방법 — GitHub에서 바로 편집

1. [GitHub 저장소](https://github.com/NAMU578/MAGIC)에 로그인합니다. (먼저 팀장에게 **협업자(Collaborator) 초대**를 받아야 합니다 — 아래 참고)
2. 수정하고 싶은 `.md` 파일을 클릭합니다. 예: 팀 소개를 고치려면 `members.md`
3. 오른쪽 위 **연필 아이콘(✏️ Edit this file)** 을 누릅니다.
4. 내용을 수정합니다.
5. 페이지 맨 아래 **Commit changes** (초록색 버튼)를 누릅니다.
6. 1~2분 뒤 홈페이지에 자동으로 반영됩니다.

## 어떤 파일을 고치면 되나요?

<div class="table-wrap" markdown="1">

| 고치고 싶은 페이지 | 편집할 파일 |
|---|---|
| 홈 화면 | `index.md` |
| 프로젝트 소개 | `introduction.md` |
| 하드웨어 설계 개요 | `hardware/index.md` |
| 하드웨어 상세 문서 | `hardware/design_package.md` |
| 연구 일정 | `timeline.md` |
| 팀 소개 | `members.md` |
| 자료실 | `downloads.md` |

</div>

## Markdown 기본 문법 (이것만 알면 충분)

```markdown
## 큰 제목
### 작은 제목

일반 문장은 그냥 씁니다.

- 목록 항목 1
- 목록 항목 2

**굵게**, 그리고 [링크 텍스트](https://example.com)

| 표 제목 1 | 표 제목 2 |
|---|---|
| 내용 | 내용 |
```

- 줄 맨 앞에 `##`, `###` 을 붙이면 제목이 됩니다.
- `-` 로 시작하면 목록이 됩니다.
- `**글자**` 는 굵게 표시됩니다.
- `[보이는 글자](주소)` 는 링크가 됩니다.

## 이미지 추가하기

1. 이미지 파일을 `assets/images/` 폴더에 업로드합니다. (GitHub에서 폴더 진입 후 **Add file → Upload files**)
2. 글 안에 이렇게 씁니다: `![설명](assets/images/파일이름.png)`

## 새 페이지 만들기

1. 저장소 최상단에서 **Add file → Create new file**
2. 파일 이름을 `새페이지.md` 처럼 짓고, 맨 위에 아래를 적습니다.

```markdown
---
title: 새 페이지 제목
---

여기에 내용을 씁니다.
```

3. 상단 메뉴에도 넣고 싶으면 `_config.yml` 파일의 `nav:` 목록에 한 줄 추가하면 됩니다.

## ⚠️ 주의 — 건드리지 않는 게 좋은 파일

다음 파일들은 홈페이지의 디자인·구조를 담당합니다. 잘 모르면 수정하지 마세요.

- `_layouts/` 폴더 (페이지 틀)
- `assets/css/style.css` (디자인)
- `_config.yml` 의 윗부분 설정 (메뉴 `nav:` 부분은 수정해도 됩니다)

## 팀장이 할 일 — 팀원을 협업자로 초대

팀원이 직접 수정하려면 저장소 협업자로 초대해야 합니다.

1. [저장소 Settings](https://github.com/NAMU578/MAGIC/settings/access) 로 이동
2. **Collaborators → Add people**
3. 팀원의 GitHub 아이디(또는 이메일)를 입력해 초대
4. 팀원이 초대 메일을 수락하면 편집 권한이 생깁니다.

> 협업자가 아니어도 누구나 **Fork → Pull Request** 방식으로 수정 제안을 보낼 수 있지만, 같은 팀이라면 협업자 초대가 가장 편합니다.

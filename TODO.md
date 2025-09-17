當使用者在repo中標註 或是 透過 `@{settings.app_slug}` 提到我的這個app 以後, 這個app會做一些對應的功能:

1. 當 issue 中提及 `@{settings.app_slug} ...` 並交代任務時, 會自動 trigger 完成任務
    - 這一個功能會透過 `Claude Code / OpenAI Codex` 去完成任務並發送PR到當前repo
    - 此功能可以支援繼續任務, 會讓使用者可以在PR發起後透過 comment 中標註 `@{settings.app_slug}` 繼續使用 `Claude Code / OpenAI Codex` 去修改當前 PR
2. 當 PR message 中帶有 `@{settings.app_slug} generate commit message`, 則會查看所有改動 並編輯 PR 的原始內容
3. 當 PR 發起時 在PR回應提及 `@{settings.app_slug} ...`, 則會將此任務當成一個 繼續工作 或是 協助接手完成, 這時候會透過 `Claude Code / OpenAI Codex` 切到當前 branch 繼續完成, 完成後 push 到當前同一個 branch 提供使用者檢查

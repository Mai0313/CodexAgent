## TODO: 更新 README.zh-TW.md

- 這個README是從其他專案模板中複製過來的 文檔部分你需要大幅度修改內容
- 目前這些功能都還沒完成, 但你可以先當作這些功能都已經完成了
    - 詳細敘述這些功能
    - 這些功能的實際流程
        - 例如 使用者標記 -> App 收到指令 -> Git clone 到 `./workspace` -> 透過 `Claude Code / OpenAI Codex` 修改代碼 -> commit changes -> 發送 `PR`
- 請查看實際代碼 如果未完成則計畫 已完成就照實際寫
- 這些功能支援 `Github / Gitea`

## 以下是實際功能

- 當使用者在repo中標註 或是 透過 `@{settings.app_slug}` 提到我的這個 app 以後...
    - 當 issue 中提及 `@{settings.app_slug} ...` 並交代任務時, 會自動 trigger 完成任務
        - 這一個功能會透過 `Claude Code / OpenAI Codex` 去完成任務並發送PR到當前repo
        - 此功能可以支援繼續任務, 會讓使用者可以在PR發起後透過 comment 中標註 `@{settings.app_slug}` 繼續使用 `Claude Code / OpenAI Codex` 去修改當前 PR
    - 當 PR 發起時 在PR回應提及 `@{settings.app_slug} ...`, 則會將此任務當成一個協助接手完成 或 繼續任務, 這時候會透過 `Claude Code / OpenAI Codex` 切到當前 branch 繼續完成, 完成後 push 到當前同一個 branch 提供使用者檢查
    - 當 PR message 中帶有 `@{settings.app_slug} generate PR message`, 則會查看所有改動 並編輯 PR 的原始內容

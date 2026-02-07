TEXTS = {
    "ru": {
        "title": "# Flux Prompt Lab: идея → промпт",
        "idea_label": "Ваша идея",
        "idea_placeholder": "Например: киберпанк, дождливая улица с неоном",
        "slider_label": "Креативность (0 = строго по идее, 10 = креативно)",
        "generate": "Сгенерировать",
        "creative": "Случайный пейзаж",
        "save_name": "Имя для сохранения",
        "save_btn": "Сохранить промпт",
        "extended_prompt": "Расширенный промпт",
        "saved_prompts": "Сохранённые записи",
        "saved_prompts_title": "Сохранённые записи",
        "load_btn": "Загрузить",
        "refresh_btn": "Обновить список",
        "delete_btn": "Удалить",
        "prompt_editor": "Промпт (редактируемый)",
        "status": "Статус",
        "copy_button_html": (
            " <button onclick=\"(function(){"
            "let textarea=document.querySelector('#prompt_editor textarea')"
            "||document.querySelector('#prompt_editor');"
            "if(!textarea){"
            "const btn=event.target;"
            "let parent=btn.parentElement;"
            "while(parent&&!textarea){"
            "textarea=parent.querySelector('textarea[rows=\\'8\\']')"
            "||parent.querySelector('textarea');"
            "parent=parent.parentElement;"
            "}"
            "}"
            "if(!textarea){"
            "const all=document.querySelectorAll('textarea');"
            "textarea=all[all.length-2]||all[all.length-1];"
            "}"
            "if(textarea)navigator.clipboard.writeText(textarea.value||'');"
            "})()\">Копировать</button> "
        ),
        "switch_lang": "EN",
    },
    "en": {
        "title": "# Flux Prompt Lab: idea → prompt",
        "idea_label": "Your idea",
        "idea_placeholder": "Eg: cyberpunk, rainy neon street",
        "slider_label": "Creativity (0 = literal, 10 = creative)",
        "generate": "Generate",
        "creative": "Random landscape",
        "save_name": "Save name",
        "save_btn": "Save prompt",
        "extended_prompt": "Extended prompt",
        "saved_prompts": "Saved prompts",
        "saved_prompts_title": "Saved prompts",
        "load_btn": "Load",
        "refresh_btn": "Refresh list",
        "delete_btn": "Delete",
        "prompt_editor": "Prompt (editable)",
        "status": "Status",
        "copy_button_html": (
            " <button onclick=\"(function(){"
            "let textarea=document.querySelector('#prompt_editor textarea')"
            "||document.querySelector('#prompt_editor');"
            "if(!textarea){"
            "const btn=event.target;"
            "let parent=btn.parentElement;"
            "while(parent&&!textarea){"
            "textarea=parent.querySelector('textarea[rows=\\'8\\']')"
            "||parent.querySelector('textarea');"
            "parent=parent.parentElement;"
            "}"
            "}"
            "if(!textarea){"
            "const all=document.querySelectorAll('textarea');"
            "textarea=all[all.length-2]||all[all.length-1];"
            "}"
            "if(textarea)navigator.clipboard.writeText(textarea.value||'');"
            "})()\">Copy</button> "
        ),
        "switch_lang": "RU",
    },
}

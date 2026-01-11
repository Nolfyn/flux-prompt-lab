import gradio as gr
from typing import Dict, Tuple, List
import llm_adapter
import storage

from utils import TEXTS


def _build_saved_choices() -> Tuple[List[str], Dict[str, str]]:
    """
    Возвращает:
      - список display-строк для Dropdown (["Name (id1234)", ...])
      - map display -> id
    """
    rows = storage.list_prompts(limit=200)
    choices = []
    mapping = {}
    for r in rows:
        display = f"{r.get('name') or 'untitled'} ({r.get('id')[:8]})"
        choices.append(display)
        mapping[display] = r.get("id")
    return choices, mapping


def generate_handler(idea: str, slider: int):
    """Обработчик нажатия кнопки «Сгенерировать»."""
    try:
        variants = llm_adapter.expand_prompt(idea or "", slider) or []
        if not variants:
            return "", "Пустой ответ от LLM"
        first = variants[0]
        prompt_text = (
            first.get("prompt") if isinstance(first, dict) else str(first)
        )
        prompt_text = (prompt_text or "").strip()
        return prompt_text, "OK"
    except Exception as e:
        return "", f"Ошибка: {e}"


def generate_random_handler(slider: int) -> Tuple[str, str]:
    """Вызов expand_prompt для рандомного результата."""
    idea = "A detailed and imaginative landscape of your choice."
    return generate_handler(idea, slider)


def save_prompt_handler(
    prompt_text: str, name: str
) -> Tuple[str, List[str], Dict[str, str]]:
    """Сохраняет промпт через storage.save_prompt."""
    if not prompt_text or not prompt_text.strip():
        return "Нечего сохранять", [], {}
    record = {
        "name": name or "untitled",
        "prompt": prompt_text,
    }
    try:
        rid = storage.save_prompt(record)
    except Exception as e:
        return f"Ошибка сохранения: {e}", [], {}
    choices, mapping = _build_saved_choices()
    return f"Сохранено: {rid}", choices, mapping


def refresh_saved_handler() -> Tuple[List[str], Dict[str, str]]:
    """Обновить список сохранённых записей."""
    choices, mapping = _build_saved_choices()
    return choices, mapping


def load_saved_handler(
    selected_display: str, mapping: Dict[str, str]
) -> Tuple[str, str]:
    """Загрузить выбранную сохранённую запись в редактор (prompt_editor)."""
    if not selected_display:
        return "", "Ничего не выбрано"
    rid = mapping.get(selected_display)
    if not rid:
        return "", "Выбранный элемент не найден"
    rec = storage.get_prompt(rid)
    if not rec:
        return "", "Запись не найдена"
    return rec.get("prompt", ""), f"Загружено: {rec.get('name')}"


def delete_saved_handler(
    selected_display: str, mapping: Dict[str, str]
) -> Tuple[str, List[str], Dict[str, str], str]:
    """
    Удалить выбранную запись. Возвращаем (status, new_choices, new_mapping,
    cleared_editor). cleared_editor — пустая строка, чтобы очистить редактор,
    если нужно.
    """
    if not selected_display:
        return "Ничего не выбрано", [], {}, ""
    rid = mapping.get(selected_display)
    if not rid:
        return "Не удалось найти id", [], {}, ""
    ok = storage.delete_prompt(rid)
    if not ok:
        return "Удаление не удалось", [], {}, ""
    # обновим список
    choices, mapping = _build_saved_choices()
    return "Удалено", choices, mapping, ""


def switch_language_handler(current_lang: str):
    """Простое переключение языка — возвращает обновления для компонентов."""
    new_lang = "en" if current_lang == "ru" else "ru"
    t = TEXTS[new_lang]
    updates = {
        "title": gr.update(value=t["title"]),
        "idea_label": gr.update(
            label=t["idea_label"], placeholder=t["idea_placeholder"]
        ),
        "slider_label": gr.update(label=t["slider_label"]),
        "generate_label": gr.update(value=t["generate"]),
        "creative_label": gr.update(value=t["creative"]),
        "save_name_label": gr.update(label=t["save_name"], placeholder=""),
        "save_btn_label": gr.update(value=t["save_btn"]),
        "saved_prompts_label": gr.update(label=t["saved_prompts"]),
        "load_btn_label": gr.update(value=t["load_btn"]),
        "refresh_btn_label": gr.update(value=t["refresh_btn"]),
        "delete_btn_label": gr.update(value=t["delete_btn"]),
        "prompt_editor_label": gr.update(label=t["prompt_editor"]),
        "status_label": gr.update(label=t["status"]),
        "copy_html": gr.update(value=t["copy_button_html"]),
        "lang_button": gr.update(value=t["switch_lang"]),
    }
    return (
        new_lang,
        updates["title"],
        updates["idea_label"],
        updates["slider_label"],
        updates["generate_label"],
        updates["creative_label"],
        updates["save_name_label"],
        updates["save_btn_label"],
        updates["saved_prompts_label"],
        updates["load_btn_label"],
        updates["refresh_btn_label"],
        updates["delete_btn_label"],
        updates["prompt_editor_label"],
        updates["status_label"],
        updates["copy_html"],
        updates["lang_button"],
    )


# --- Gradio UI ---
with gr.Blocks() as demo:
    lang_state = gr.State("ru")
    saved_map_state = gr.State({})

    txt = TEXTS["ru"]

    heading_md = gr.Markdown(txt["title"])

    with gr.Row():
        with gr.Column(scale=2):
            idea_input = gr.Textbox(
                label=txt["idea_label"],
                placeholder=txt["idea_placeholder"],
                lines=2,
            )
            slider = gr.Slider(
                minimum=0,
                maximum=10,
                step=1,
                label=txt["slider_label"],
                value=5,
            )
            with gr.Row():
                generate_btn = gr.Button(txt["generate"])
                creative_btn = gr.Button(txt["creative"])
            save_name = gr.Textbox(
                label=txt["save_name"], placeholder="", lines=1
            )
            save_btn = gr.Button(txt["save_btn"])

            # блок сохранённых записей
            gr.Markdown("### " + txt["saved_prompts"])
            saved_dropdown = gr.Dropdown(
                label=txt["saved_prompts"], choices=[], interactive=True
            )
            with gr.Row():
                load_btn = gr.Button(txt["load_btn"])
                refresh_btn = gr.Button(txt["refresh_btn"])
                delete_btn = gr.Button(txt["delete_btn"])

            # кнопка переключения языка
            lang_btn = gr.Button(txt["switch_lang"])

        with gr.Column(scale=3):
            gr.Markdown("### Расширенный промпт")
            prompt_editor = gr.Textbox(
                label=txt["prompt_editor"], lines=8, elem_id="prompt_editor"
            )
            copy_html = gr.HTML(txt["copy_button_html"])
            status = gr.Textbox(label=txt["status"], interactive=False)

    # --- Привязки ---
    # Генерировать (основная кнопка)
    generate_btn.click(
        fn=generate_handler,
        inputs=[idea_input, slider],
        outputs=[prompt_editor, status],
    )

    # Кнопка "Креатив"
    creative_btn.click(
        fn=generate_random_handler,
        inputs=[slider],
        outputs=[prompt_editor, status],
    )

    # Сохранение — возвращает статус и обновляет список сохранённых
    save_btn.click(
        fn=save_prompt_handler,
        inputs=[prompt_editor, save_name],
        outputs=[status, saved_dropdown, saved_map_state],
    )

    # Обновить список
    refresh_btn.click(
        fn=refresh_saved_handler,
        inputs=[],
        outputs=[saved_dropdown, saved_map_state],
    )

    # Загрузить выбранную запись
    load_btn.click(
        fn=load_saved_handler,
        inputs=[saved_dropdown, saved_map_state],
        outputs=[prompt_editor, status],
    )

    # Удалить выбранную запись
    delete_btn.click(
        fn=delete_saved_handler,
        inputs=[saved_dropdown, saved_map_state],
        outputs=[status, saved_dropdown, saved_map_state, prompt_editor],
    )

    # Переключение языка (возвращаем много обновлений)
    lang_btn.click(
        fn=switch_language_handler,
        inputs=[lang_state],
        outputs=[
            lang_state,
            heading_md,
            idea_input,
            slider,
            generate_btn,
            creative_btn,
            save_name,
            save_btn,
            saved_dropdown,
            load_btn,
            refresh_btn,
            delete_btn,
            prompt_editor,
            status,
            copy_html,
            lang_btn,
        ],
    )

if __name__ == "__main__":
    demo.launch()

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
    try:
        rows = storage.list_prompts(limit=200)
        choices = []
        mapping = {}
        for r in rows:
            record_id = r.get("id")
            if not record_id:
                continue
            display = f"{r.get('name') or 'untitled'} ({record_id[:8]})"
            choices.append(display)
            mapping[display] = record_id
        return choices, mapping
    except Exception as e:
        print(f"Error in _build_saved_choices: {e}")
        return [], {}


def generate_handler(idea: str, slider: int):
    """Обработчик нажатия кнопки «Сгенерировать»."""
    try:
        variants = llm_adapter.expand_prompt(idea or "", slider) or []
        if not variants:
            return (
                "",
                "Empty LLM response",
                gr.update(interactive=True),  # generate_btn
                gr.update(interactive=True),  # creative_btn
                gr.update(interactive=True),  # idea_input
                gr.update(interactive=True),  # slider
            )
        first = variants[0]
        prompt_text = (
            first.get("prompt") if isinstance(first, dict) else str(first)
        )
        prompt_text = (prompt_text or "").strip()
        return (
            prompt_text,
            "Done",
            gr.update(interactive=True),  # generate_btn
            gr.update(interactive=True),  # creative_btn
            gr.update(interactive=True),  # idea_input
            gr.update(interactive=True),  # slider
        )
    except Exception as e:
        return (
            "",
            f"Error: {e}",
            gr.update(interactive=True),  # generate_btn
            gr.update(interactive=True),  # creative_btn
            gr.update(interactive=True),  # idea_input
            gr.update(interactive=True),  # slider
        )


def generate_random_handler(slider: int):
    """Вызов expand_prompt для получения случайного пейзажа."""
    idea = "A detailed and imaginative landscape of your choice."
    return generate_handler(idea, slider)


def save_prompt_handler(
    prompt_text: str, name: str
) -> Tuple[str, gr.update, Dict[str, str]]:
    """Сохраняет промпт через storage.save_prompt."""
    if not prompt_text or not prompt_text.strip():
        choices, mapping = _build_saved_choices()
        return "Нечего сохранять", gr.update(choices=choices), mapping
    record = {
        "name": name or "untitled",
        "prompt": prompt_text,
    }
    try:
        rid = storage.save_prompt(record)
    except Exception as e:
        choices, mapping = _build_saved_choices()
        return f"Ошибка сохранения: {e}", gr.update(choices=choices), mapping
    choices, mapping = _build_saved_choices()
    return f"Сохранено: {rid}", gr.update(choices=choices), mapping


def refresh_saved_handler() -> Tuple[gr.update, Dict[str, str]]:
    """Обновить список сохранённых записей."""
    try:
        choices, mapping = _build_saved_choices()
        return gr.update(choices=choices), mapping
    except Exception as e:
        print(f"Error in refresh_saved_handler: {e}")
        return gr.update(choices=[]), {}


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
) -> Tuple[str, gr.update, Dict[str, str], str]:
    """
    Удалить выбранную запись. Возвращаем (status, new_choices, new_mapping,
    cleared_editor). cleared_editor — пустая строка, чтобы очистить редактор,
    если нужно.
    """
    if not selected_display:
        choices, mapping = _build_saved_choices()
        return "Ничего не выбрано", gr.update(choices=choices), mapping, ""
    rid = mapping.get(selected_display)
    if not rid:
        choices, mapping = _build_saved_choices()
        return "Не удалось найти id", gr.update(choices=choices), mapping, ""
    try:
        ok = storage.delete_prompt(rid)
        if not ok:
            choices, mapping = _build_saved_choices()
            return (
                "Удаление не удалось",
                gr.update(choices=choices),
                mapping,
                "",
            )
        choices, mapping = _build_saved_choices()
        return "Удалено", gr.update(choices=choices), mapping, ""
    except Exception as e:
        choices, mapping = _build_saved_choices()
        return f"Ошибка удаления: {e}", gr.update(choices=choices), mapping, ""


def switch_language_handler(current_lang: str):
    """Переключение языка — возвращает обновления для компонентов."""
    new_lang = "en" if current_lang == "ru" else "ru"
    t = TEXTS[new_lang]
    return (
        new_lang,
        gr.update(value=t["title"]),
        gr.update(label=t["idea_label"], placeholder=t["idea_placeholder"]),
        gr.update(label=t["slider_label"]),
        gr.update(value=t["generate"]),
        gr.update(value=t["creative"]),
        gr.update(label=t["save_name"], placeholder=""),
        gr.update(value=t["save_btn"]),
        gr.update(value="### " + t["saved_prompts_title"]),
        gr.update(label=t["saved_prompts"]),
        gr.update(value=t["load_btn"]),
        gr.update(value=t["refresh_btn"]),
        gr.update(value=t["delete_btn"]),
        gr.update(value="### " + t["extended_prompt"]),
        gr.update(label=t["prompt_editor"]),
        gr.update(label=t["status"]),
        gr.update(value=t["copy_button_html"]),
        gr.update(value=t["switch_lang"]),
    )


# --- Gradio UI ---
with gr.Blocks() as demo:
    lang_state = gr.State("ru")
    # Initialize saved_map_state with initial mapping
    initial_choices, initial_mapping = _build_saved_choices()
    saved_map_state = gr.State(initial_mapping)

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
            saved_prompts_title_md = gr.Markdown(
                "### " + txt["saved_prompts_title"]
            )
            saved_dropdown = gr.Dropdown(
                label=txt["saved_prompts"],
                choices=initial_choices,
                interactive=True,
            )
            with gr.Row():
                load_btn = gr.Button(txt["load_btn"])
                refresh_btn = gr.Button(txt["refresh_btn"])
                delete_btn = gr.Button(txt["delete_btn"])

            # кнопка переключения языка
            lang_btn = gr.Button(txt["switch_lang"])

        with gr.Column(scale=3):
            extended_prompt_md = gr.Markdown("### " + txt["extended_prompt"])
            prompt_editor = gr.Textbox(
                label=txt["prompt_editor"], lines=8, elem_id="prompt_editor"
            )
            copy_html = gr.HTML(txt["copy_button_html"])
            status = gr.Textbox(label=txt["status"], interactive=False)

    # --- Привязки ---
    # Генерировать (основная кнопка)
    def generate_with_loading(idea: str, slider: int):
        """Обертка для генерации (с отключением элементов управления)."""
        yield (
            "",
            "Generating",
            gr.update(interactive=False),  # generate_btn
            gr.update(interactive=False),  # creative_btn
            gr.update(interactive=False),  # idea_input
            gr.update(interactive=False),  # slider
        )
        result = generate_handler(idea, slider)
        yield result

    generate_btn.click(
        fn=generate_with_loading,
        inputs=[idea_input, slider],
        outputs=[
            prompt_editor,
            status,
            generate_btn,
            creative_btn,
            idea_input,
            slider,
        ],
    )

    # Кнопка "Креатив"
    def generate_random_with_loading(slider: int):
        """
        Обертка для случайной генерации (с отключением элементов управления).
        """
        idea = "A detailed and imaginative landscape of your choice."
        yield (
            "",
            "Generating",
            gr.update(interactive=False),  # generate_btn
            gr.update(interactive=False),  # creative_btn
            gr.update(interactive=False),  # idea_input
            gr.update(interactive=False),  # slider
        )
        # Выполняем генерацию
        result = generate_handler(idea, slider)
        yield result

    creative_btn.click(
        fn=generate_random_with_loading,
        inputs=[slider],
        outputs=[
            prompt_editor,
            status,
            generate_btn,
            creative_btn,
            idea_input,
            slider,
        ],
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

    # Переключение языка (возвращаем обновления)
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
            saved_prompts_title_md,
            saved_dropdown,
            load_btn,
            refresh_btn,
            delete_btn,
            extended_prompt_md,
            prompt_editor,
            status,
            copy_html,
            lang_btn,
        ],
    )

if __name__ == "__main__":
    demo.launch()

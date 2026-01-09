import gradio as gr
from typing import Dict
import llm_adapter
import storage


def generate_handler(idea: str, slider: int):
    """Обработчик нажатия кнопки «Сгенерировать»."""
    variants = llm_adapter.expand_prompt(idea, slider) or []
    processed = []
    for i, v in enumerate(variants):
        label = v.get("variant") or f"variant_{i + 1}"
        prompt_text = v.get("prompt", "").strip()
        processed.append(
            {
                "label": label,
                "prompt": prompt_text,
            }
        )

    labels = [v["label"] for v in processed]
    prompt_map = {v["label"]: v["prompt"] for v in processed}
    return labels, prompt_map


def on_variant_select(selected_label: str, prompt_map: Dict):
    """Возвращает выбранный промпт."""
    if not selected_label:
        return ""
    return prompt_map.get(selected_label, "")


def save_prompt_handler(
    prompt_text: str, name: str
):
    """Сохраняет промпт через storage.save_prompt."""
    record = {
        "name": name or "untitled",
        "prompt": prompt_text,
    }
    saved_id = storage.save_prompt(record)
    return f"Сохранено: {saved_id}"


# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# Flux Prompt Lab — идея → промпт")

    with gr.Row():
        with gr.Column(scale=2):
            idea_input = gr.Textbox(
                label="Ваша идея",
                placeholder="Например: киберпанк, дождливая улица с неоном",
                lines=2,
            )
            slider = gr.Slider(
                minimum=0,
                maximum=10,
                step=1,
                label="Креативность (0 = строго по идее, 10 = креативно)",
                value=5,
            )
            generate_btn = gr.Button("Сгенерировать")

            save_name = gr.Textbox(
                label="Имя для сохранения",
                placeholder="Например: Cyberpunk city v1",
            )
            save_btn = gr.Button("Сохранить промпт")

        with gr.Column(scale=3):
            gr.Markdown("### Расширенный промпт")
            variants_dropdown = gr.Dropdown(
                label="Варианты", choices=[], interactive=True
            )
            prompt_editor = gr.Textbox(label="Промпт (редактируемый)", lines=6)
            status = gr.Textbox(label="Статус", interactive=False)

    prompt_map_state = gr.State({})

    generate_btn.click(
        fn=generate_handler,
        inputs=[idea_input, slider],
        outputs=[
            variants_dropdown,
            prompt_map_state,
        ],
    )
    variants_dropdown.change(
        fn=on_variant_select,
        inputs=[variants_dropdown, prompt_map_state],
        outputs=[prompt_editor],
    )

    save_btn.click(
        fn=save_prompt_handler,
        inputs=[
            prompt_editor,
            save_name,
        ],
        outputs=[status],
    )

if __name__ == "__main__":
    demo.launch()

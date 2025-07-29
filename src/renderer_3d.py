# src/renderer_3d.py

import matplotlib

matplotlib.use(
    "Agg"
)  # Usa o backend 'Agg' que não requer uma GUI, essencial para Flet.
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io
import cv2
from src.utils import get_logger

# Obtém uma instância do logger para este módulo.
logger = get_logger(__name__)

# Mapeamento de conexões para o esqueleto 3D, usando os nomes dos landmarks.
# Isso nos permite desenhar os "ossos" conectando as articulações corretas.
POSE_CONNECTIONS_3D = [
    ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
    ("LEFT_SHOULDER", "LEFT_ELBOW"),
    ("LEFT_ELBOW", "LEFT_WRIST"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    ("RIGHT_ELBOW", "RIGHT_WRIST"),
    ("LEFT_SHOULDER", "LEFT_HIP"),
    ("RIGHT_SHOULDER", "RIGHT_HIP"),
    ("LEFT_HIP", "RIGHT_HIP"),
    ("LEFT_HIP", "LEFT_KNEE"),
    ("LEFT_KNEE", "LEFT_ANKLE"),
    ("RIGHT_HIP", "RIGHT_KNEE"),
    ("RIGHT_KNEE", "RIGHT_ANKLE"),
]

# Define quais conexões pertencem a cada lado para a colorização.
LEFT_CONNECTIONS_3D = {
    tuple(sorted(conn))
    for conn in POSE_CONNECTIONS_3D
    if "LEFT" in conn[0] and "LEFT" in conn[1]
}
RIGHT_CONNECTIONS_3D = {
    tuple(sorted(conn))
    for conn in POSE_CONNECTIONS_3D
    if "RIGHT" in conn[0] and "RIGHT" in conn[1]
}


def render_3d_skeleton(landmarks_list: list) -> np.ndarray:
    """
    Renderiza um esqueleto 3D a partir de uma lista de landmarks usando Matplotlib.

    Args:
        landmarks_list (list): Uma lista de dicionários, onde cada dicionário representa um landmark
                               com as chaves 'x', 'y', 'z', 'visibility', e 'name'.

    Returns:
        np.ndarray: Uma imagem (em formato numpy array BGR) do esqueleto 3D renderizado,
                    pronta para ser exibida pelo OpenCV ou Flet.
    """
    # Se não houver landmarks, retorna uma imagem preta vazia.
    if not landmarks_list:
        logger.warning(
            "Tentativa de renderizar esqueleto 3D com lista de landmarks vazia. Retornando imagem vazia."
        )
        return np.zeros((640, 640, 3), dtype=np.uint8)

    # Cria uma figura e um eixo 3D para o gráfico. Define a cor de fundo.
    fig = plt.figure(figsize=(8, 8), dpi=80)
    fig.patch.set_facecolor("black")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("black")

    # Itera sobre as conexões para desenhar os ossos.
    for p1_name, p2_name in POSE_CONNECTIONS_3D:
        p1 = next((lm for lm in landmarks_list if lm["name"] == p1_name), None)
        p2 = next((lm for lm in landmarks_list if lm["name"] == p2_name), None)

        if p1 and p2 and p1["visibility"] > 0.5 and p2["visibility"] > 0.5:
            # Define a cor da linha com base no lado do corpo.
            connection = tuple(sorted((p1_name, p2_name)))
            if connection in LEFT_CONNECTIONS_3D:
                color = "orange"
            elif connection in RIGHT_CONNECTIONS_3D:
                color = "#0077FF"  # Azul mais vibrante
            else:
                color = "white"

            # Desenha a linha (osso) conectando os dois pontos.
            # A ordem dos eixos é trocada (z, y) para uma visualização mais intuitiva (profundidade).
            ax.plot(
                [-p1["x"], -p2["x"]],
                [-p1["z"], -p2["z"]],
                [-p1["y"], -p2["y"]],
                color=color,
                linewidth=3,
            )

    # --- Configurações de Câmera e Aparência do Gráfico ---
    ax.view_init(elev=20, azim=-75)
    ax.set_box_aspect(
        [1, 1, 1]
    )  # Garante que a escala seja consistente em todos os eixos.
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.set_zlim([-0.5, 0.5])

    # Remove o fundo, eixos e grades para uma visualização limpa.
    plt.axis("off")

    # --- Converte o Gráfico em uma Imagem OpenCV ---
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, facecolor="black")
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    plt.close(fig)

    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    logger.debug("Renderização 3D do esqueleto concluída com sucesso.")
    return img

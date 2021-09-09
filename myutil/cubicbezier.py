def cubicbezier(x1, y1, x2, y2):
    """
    Cubic-Bezierの値を計算する関数を生成する関数
    """
    cx = 3 * x1
    bx = 3 * (x2 - x1) - cx
    ax = 1 - cx - bx
    cy = 3 * y1
    by = 3 * (y2 - y1) - cy
    ay = 1 - cy - by

    def bezierX(t):     # 媒介変数表示したX座標
        return t * (cx + t * (bx + t * ax))

    def bezierDX(t):    # X座標のt微分
        return cx + t * (2 * bx + 3 * ax * t)

    def newtonRaphson(x):  # ニュートン法で数値解析する
        if x <= 0:
            return 0
        if x >= 1:
            return 1
        t = x
        while True:
            prev = t
            t = t - (bezierX(t) - x) / bezierDX(t)
            if abs(t - prev) <= 1e-4:   # 1e-2 程度でも良い
                return t

    def f(t):
        # X座標(時刻)に対応する媒介変数tの値を取得する
        t = newtonRaphson(t)
        # Y座標(Easing量)を計算する
        return t * (cy + t * (by + t * ay))

    return f

def calcular_presupuesto(ancho, alto, precio_m2):
    if not ancho or not alto or not precio_m2:
        return 0
    area_m2 = (ancho / 100) * (alto / 100)
    total = area_m2 * precio_m2
    return round(total, 2)

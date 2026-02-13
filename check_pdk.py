import pydeck as pdk
try:
    print(f"CARTO_DARK: {pdk.map_style.CARTO_DARK}")
except AttributeError:
    print("pdk.map_style.CARTO_DARK not found")
    print(dir(pdk))
except Exception as e:
    print(e)

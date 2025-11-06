import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Többszörös fiókellenőrzés", page_icon="🔍")

st.title("🔍 Többszörös fiókellenőrző eszköz")

st.markdown("### 1️⃣ Töltsd fel a **Korábban törölt játékosok (Deleted Players)** CSV fájlt")

deleted_file = st.file_uploader("Korábban töröltek CSV feltöltése", type="csv")

if deleted_file:
    deleted_df = pd.read_csv(deleted_file)

    if 'Personal ID' not in deleted_df.columns:
        st.error("❌ A feltöltött fájlban nincs 'Personal ID' oszlop.")
    else:
        deleted_df['Personal ID'] = (
            deleted_df['Personal ID']
            .astype(str)
            .str.replace(r'_adatved|_adatve|_adatv', '', regex=True)
        )

        st.success("✅ Deleted Players fájl sikeresen beolvasva és megtisztítva.")

        st.markdown("### 2️⃣ Töltsd fel a **Tegnap regisztráltak** CSV fájlt")

        new_file = st.file_uploader("Tegnap regisztráltak CSV feltöltése", type="csv")

        if new_file:
            new_df = pd.read_csv(new_file)

            if not {'Personal ID', 'User ID'}.issubset(new_df.columns):
                st.error("❌ A második fájlban nincs meg mindkét oszlop: 'Personal ID' és 'User ID'.")
            else:
                total_regs = len(new_df)
                matches = new_df[new_df['Personal ID'].isin(deleted_df['Personal ID'])]
                match_count = len(matches)

                st.markdown("### 📊 Eredmények")
                st.write(f"**Összes új regisztráció:** {total_regs}")
                st.write(f"**Ebből korábban töröltek között szerepel:** {match_count}")

                if match_count > 0:
                    st.markdown("### ⚠️ Egyező felhasználók listája")
                    st.dataframe(matches[['User ID', 'Personal ID']])

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        matches.to_excel(writer, index=False, sheet_name='Egyezések')
                    excel_data = output.getvalue()

                    st.download_button(
                        label="⬇️ Eredmény letöltése Excelként",
                        data=excel_data,
                        file_name="egyezesek.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("✅ Nincs egyezés a két fájl között.")

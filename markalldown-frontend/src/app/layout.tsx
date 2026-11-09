import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MarkAllDown — Konversi file ke Markdown",
  description:
    "Konversi PDF, DOCX, PPTX, XLSX, HTML, dan banyak format lainnya ke Markdown dengan cepat. Dukung konversi URL dan YouTube.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        {/* Script inline untuk mencegah flash saat dark mode — FR-23, AC-21 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  if (theme === 'dark' || (!theme && prefersDark) || theme === 'system' && prefersDark) {
                    document.documentElement.classList.add('dark');
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}

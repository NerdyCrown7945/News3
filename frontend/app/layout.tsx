import { Nav } from "../components/Nav";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body style={{ fontFamily: "sans-serif", padding: 20, maxWidth: 960, margin: "0 auto" }}>
        <h1>AI · ScienceTech 브리핑</h1>
        <Nav />
        {children}
      </body>
    </html>
  );
}

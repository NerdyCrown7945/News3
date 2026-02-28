import Link from "next/link";

const links = [
  ["/", "News"],
  ["/clusters", "Clusters"],
  ["/trends", "Trends"],
  ["/planning", "Planning"],
] as const;

export function Nav() {
  return (
    <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
      {links.map(([href, label]) => (
        <Link key={href} href={href}>{label}</Link>
      ))}
    </nav>
  );
}

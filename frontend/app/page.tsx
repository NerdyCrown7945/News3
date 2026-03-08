import { NewsList } from "../components/NewsList";
import { loadFeed } from "../lib/data";

export default async function Home() {
  const { items, fallback } = await loadFeed();
  return <NewsList items={items} fallback={fallback} />;
}

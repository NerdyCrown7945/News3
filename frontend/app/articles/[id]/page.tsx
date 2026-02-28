import { loadArticle } from "../../../lib/data";

export default async function ArticlePage({ params }: { params: { id: string } }) {
  const article = await loadArticle(params.id);
  return (
    <article>
      <h2>{article.title}</h2>
      <p>{article.summary_ko}</p>
      <ul>{article.key_points?.map((p, i) => <li key={i}>{p}</li>)}</ul>
      {article.is_valid_source_url ? (
        <a href={article.canonical_url} target="_blank">원문 보기</a>
      ) : (
        <p>원문 링크 없음</p>
      )}
    </article>
  );
}

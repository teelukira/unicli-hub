---
description: "프론트엔드를 빌드하고 S3에 배포한 후 CloudFront 캐시를 무효화합니다."
---

# Frontend 배포

프론트엔드를 빌드하고 dev-light S3 + CloudFront에 배포합니다.

## 절차

1. 빌드: `cd frontend && npm run build`
2. S3 sync: `aws s3 sync dist/ s3://tgoim-dev-frontend-336435944933 --delete --profile idcube-dev --region ap-northeast-2`
3. CloudFront invalidation: `aws cloudfront create-invalidation --distribution-id $(cd infra/dev-light && terraform output -raw cloudfront_distribution_id) --paths "/*" --profile idcube-dev`
4. 확인: `curl -s -o /dev/null -w "HTTP %{http_code}" $(cd infra/dev-light && terraform output -raw frontend_url)/`

## 엔드포인트
URL은 배포마다 변경됨 — `cd infra/dev-light && terraform output` 으로 확인

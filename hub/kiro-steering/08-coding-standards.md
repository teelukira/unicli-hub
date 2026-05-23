---
inclusion: auto
---

# 코딩 표준 및 규칙

## 언어 및 프레임워크
- Java 21 + Spring Boot 3.4.x
- React 18 + TypeScript + Vite
- 한국어 주석 허용, 코드는 영문
- 포맷터: Google Java Format (AOSP 4-space), Prettier (frontend)

## Java 코드 컨벤션 (Checkstyle 강제, maxWarnings=0)

프로젝트는 `config/checkstyle/checkstyle.xml`로 Checkstyle을 강제하며, **경고 0개 정책**(maxWarnings=0)이다. 코드 생성 시 아래 규칙을 반드시 준수해야 한다.

### Import 규칙 (가장 빈번한 위반)
- **Star import 절대 금지**: `import x.y.z.*` 사용 불가 → 개별 클래스를 명시적으로 import
- **Unused import 금지**: 사용하지 않는 import 문 남기지 않음
- **Redundant import 금지**: `java.lang.*` 등 불필요한 import 제거
- Static import도 동일 규칙 적용: `import static org.mockito.Mockito.*` 금지 → `import static org.mockito.Mockito.when` 등 개별 지정

```java
// ❌ 금지
import jakarta.persistence.*;
import com.skt.tgoim.resource.domain.model.*;
import static org.assertj.core.api.Assertions.*;

// ✅ 올바른 방식
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import com.skt.tgoim.resource.domain.model.Resource;
import com.skt.tgoim.resource.domain.model.ResourceStatus;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
```

### Import 순서
1. `com.skt.tgoim.*` (프로젝트)
2. 서드파티 (`org.springframework`, `io.restassured`, `net.jqwik` 등)
3. `java.*` / `javax.*`
4. `static` import은 파일 하단에 별도 그룹

### 포맷팅 규칙
- **인덴트**: 4 spaces (탭 금지)
- **최대 줄 길이**: 150자 (import/package/URL 제외)
- **중괄호 위치 (LeftCurly)**: 동일 줄에 시작, 내용은 다음 줄부터 — 한 줄 메서드에서도 `{` 뒤에 줄바꿈
- **메서드 사이 빈 줄 (EmptyLineSeparator)**: 필드 간은 빈 줄 없이 가능, 메서드 간은 반드시 빈 줄 1개
- **어노테이션 위치 (AnnotationLocation)**: 파라미터 없는 어노테이션은 같은 줄 가능, 파라미터 있는 어노테이션은 반드시 독립 줄

```java
// ❌ 금지 — 메서드 본문이 { 와 같은 줄
public int size() { return items.size(); }

// ✅ 올바른 방식
public int size() {
    return items.size();
}

// ❌ 금지 — 메서드 사이 빈 줄 없음
public void foo() { ... }
public void bar() { ... }

// ✅ 올바른 방식
public void foo() {
    ...
}

public void bar() {
    ...
}

// ❌ 금지 — 파라미터 있는 어노테이션이 같은 줄
@SuppressWarnings("unchecked") public Object assemble(...) { ... }

// ✅ 올바른 방식
@SuppressWarnings("unchecked")
public Object assemble(...) {
    ...
}
```

### 네이밍 규칙
- **패키지**: 소문자만 (`com.skt.tgoim.resource`)
- **클래스/인터페이스**: PascalCase (`ResourceService`, `ResourcePort`)
- **메서드**: camelCase, 밑줄 허용 (`shouldSaveResource`)
- **상수**: UPPER_SNAKE_CASE (`BASE_HREF`), logger 예외 (`log`, `logger`)
- **변수/파라미터**: camelCase

### 코딩 규칙
- **switch에 default 필수** (MissingSwitchDefault)
- **equals/hashCode 쌍 구현** (EqualsHashCode)
- **한 줄에 한 문장** (OneStatementPerLine)
- **한 선언에 한 변수** (MultipleVariableDeclarations)
- **수식어 순서**: `public static final` (ModifierOrder)
- **불필요한 수식어 제거**: interface 메서드의 `public abstract` 등 (RedundantModifier)

### JPA Entity 필수 패턴
- 모든 엔티티에 감사 필드: `createdAt`, `createdBy`, `modifiedAt`, `modifiedBy`
- `modifiedAt`/`modifiedBy`는 생성 시점에도 초기값 설정 (null 방지)
- `@Version`으로 낙관적 잠금
- `changedBy` 등 이력 필드도 빠뜨리지 않을 것

## TypeScript/React 코드 컨벤션 (ESLint strict + Prettier)

### ESLint 규칙
- **미사용 변수 금지**: `@typescript-eslint/no-unused-vars` (error) — 사용하지 않는 변수는 `_` 접두사 부여
- **Hooks 규칙 강제**: `react-hooks/rules-of-hooks` (error), `exhaustive-deps` (warn)
- strict 모드: `tseslint.configs.strict` 전체 적용

```typescript
// ❌ 금지
const chart = page.locator('canvas');  // 이후 사용 안 함

// ✅ 올바른 방식
const _chart = page.locator('canvas');  // 의도적 미사용: _ 접두사
```

### Prettier 규칙
- 포맷팅은 Prettier가 담당, ESLint와 충돌 방지를 위해 `eslint-config-prettier` 사용
- 저장 시 자동 포맷

## API 설계
- TMF Open API 표준 준수 (RESTful)
- API URL: `/{apiName}/v{major}/{resource}` (예: `/resourceInventoryManagement/v4/resource`)
- 응답 형식: JSON, TMF 표준 스키마
- 에러 응답: `{ code, reason, message, status?, referenceError? }`
- SKT 커스텀 API: `/skt/{serviceName}/v1/{resource}`

## 마이크로서비스 패턴
- 서비스 간 통신: Kafka (비동기), REST (동기)
- API Gateway: Kong (인증, 라우팅, 레이트리밋)
- 서비스 디스커버리: Kubernetes DNS
- Circuit Breaker: Resilience4j
- 인프라 의존 빈 조건부 로딩: `@ConditionalOnProperty`로 환경별 비활성화

## 데이터베이스
- PostgreSQL 16: 관계형 데이터 (SID 기반 모델)
- Neo4j: 토폴로지/그래프 데이터
- Flyway: DB 마이그레이션

## 테스트
- 단위 테스트: JUnit 5 + Mockito (Backend), Vitest + RTL (Frontend)
- 통합 테스트: Testcontainers
- API 테스트: REST Assured
- 속성 기반 테스트: jqwik PBT
- E2E 테스트: Playwright
- `data-testid` 속성 필수 (UI 자동화)

## 보안
- Zero Trust 아키텍처
- Keycloak OIDC/OAuth2
- RBAC 기반 권한 관리

## AWS 금지 패턴 (Terraform / CLI 공통)

아래 패턴은 코드 생성·리뷰 시 절대 사용하지 않는다.

### S3
- `block_public_acls = false` 등 Public Access Block 해제 금지
- `Principal = "*"` 또는 `Principal = {"AWS": "*"}` 버킷 정책 금지
- S3 Website Endpoint를 CloudFront origin으로 사용 금지 → OAC + bucket regional domain 사용
- `acl = "public-read"` / `acl = "public-read-write"` 금지

### IAM
- `Effect: Allow, Action: "*", Resource: "*"` 와일드카드 정책 금지
- 인라인 정책보다 관리형 정책(Managed Policy) 우선 사용

### 네트워크
- Security Group에 `0.0.0.0/0` inbound 허용은 ALB 80/443 포트만 예외 허용, 그 외 금지
- RDS/ElastiCache 등 데이터 스토어에 public access 금지

### 일반
- 리소스 생성 시 태그 필수 (Project, Environment, ManagedBy)
- 시크릿/비밀번호를 Terraform 변수 기본값이나 코드에 하드코딩 금지 → SSM Parameter Store 또는 Secrets Manager 사용

## 코드 구조 (Hexagonal Architecture 마이크로서비스)
```
{service-name}/
├── domain/src/main/java/com/skt/tgoim/{service}/domain/
│   ├── model/         # Domain Models (SID 기반)
│   ├── service/       # Business Logic (UseCase 구현)
│   ├── port/in/       # Inbound Port (인터페이스)
│   └── port/out/      # Outbound Port (인터페이스)
├── api/src/main/java/com/skt/tgoim/{service}/api/
│   ├── controller/    # REST Controllers
│   ├── dto/tmf/       # TMF 표준 DTO
│   ├── dto/skt/       # SKT 확장 DTO
│   └── mapper/        # DTO ↔ Domain 변환
├── infrastructure/src/main/java/com/skt/tgoim/{service}/infrastructure/
│   ├── persistence/   # JPA Entity, Repository Adapter
│   ├── messaging/     # Kafka Publisher/Consumer
│   ├── external/      # Feign Client
│   └── config/        # Infrastructure Config
├── app/src/main/
│   ├── java/.../      # Application, Boot Config
│   └── resources/
│       ├── application.yml
│       └── db/migration/  # Flyway scripts
├── build.gradle.kts
└── gradle/libs.versions.toml
```

## Pre-commit Hooks (자동 검증)
커밋 시 아래 검사가 자동 실행되며, 하나라도 실패하면 커밋이 차단된다:
1. `trim-trailing-whitespace` — 후행 공백 제거
2. `end-of-file-fixer` — 파일 끝 개행 보장
3. `check-yaml` / `check-json` — YAML/JSON 구문 검증
4. `Google Java Format (AOSP 4-space)` — Java 포맷 자동 교정
5. `Checkstyle (maxWarnings=0)` — Java 정적 분석 (경고 0개 정책)
6. `ESLint (strict)` — TypeScript/React 린트
7. `Prettier` — 프론트엔드 포맷

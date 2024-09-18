#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import inspect
import random
import factory

from factory.alchemy import SESSION_PERSISTENCE_COMMIT, SESSION_PERSISTENCE_FLUSH
from factory.builder import BuildStep, StepBuilder, parse_declarations
from sqlalchemy.ext.asyncio import async_object_session

from argilla_server.enums import DatasetDistributionStrategy, FieldType, MetadataPropertyType, OptionsOrder
from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    QuestionType,
    Record,
    Response,
    Suggestion,
    User,
    UserRole,
    Vector,
    VectorSettings,
    Workspace,
    WorkspaceUser,
    Webhook,
)
from argilla_server.models.base import DatabaseModel

from tests.database import SyncTestSession, TestSession


# https://github.com/FactoryBoy/factory_boy/issues/679#issuecomment-1348746070
class AsyncSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    async def _generate(cls, strategy, params):
        if cls._meta.abstract:
            raise factory.errors.FactoryError(
                "Cannot generate instances of abstract factory %(f)s; "
                "Ensure %(f)s.Meta.model is set and %(f)s.Meta.abstract "
                "is either not set or False." % dict(f=cls.__name__)
            )

        step = AsyncStepBuilder(cls._meta, params, strategy)
        return await step.build()

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        for key, value in kwargs.items():
            if inspect.isawaitable(value):
                kwargs[key] = await value
            if isinstance(value, DatabaseModel):
                old_session = async_object_session(value)
                session = cls._meta.sqlalchemy_session.registry().sync_session
                if old_session.sync_session.hash_key != session.hash_key:
                    old_session.expunge(value)
                    value = await old_session.merge(value)
        return await super()._create(model_class, *args, **kwargs)

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _save(cls, model_class, session, args, kwargs):
        session_persistence = cls._meta.sqlalchemy_session_persistence
        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()
        return obj


class AsyncStepBuilder(StepBuilder):
    # Redefine build function that await for instance creation and awaitable postgenerations
    async def build(self, parent_step=None, force_sequence=None):
        pre, post = parse_declarations(
            self.extras,
            base_pre=self.factory_meta.pre_declarations,
            base_post=self.factory_meta.post_declarations,
        )

        if force_sequence is not None:
            sequence = force_sequence
        elif self.force_init_sequence is not None:
            sequence = self.force_init_sequence
        else:
            sequence = self.factory_meta.next_sequence()

        step = BuildStep(
            builder=self,
            sequence=sequence,
            parent_step=parent_step,
        )
        step.resolve(pre)

        args, kwargs = self.factory_meta.prepare_arguments(step.attributes)

        instance = await self.factory_meta.instantiate(
            step=step,
            args=args,
            kwargs=kwargs,
        )

        postgen_results = {}
        for declaration_name in post.sorted():
            declaration = post[declaration_name]
            declaration_result = declaration.declaration.evaluate_post(
                instance=instance,
                step=step,
                overrides=declaration.context,
            )
            if inspect.isawaitable(declaration_result):
                declaration_result = await declaration_result
            postgen_results[declaration_name] = declaration_result

        self.factory_meta.use_postgeneration_results(
            instance=instance,
            step=step,
            results=postgen_results,
        )
        return instance


class BaseFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = TestSession
        sqlalchemy_session_persistence = "flush"


class BaseSyncFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SyncTestSession
        sqlalchemy_session_persistence = "flush"


class WorkspaceUserFactory(BaseFactory):
    class Meta:
        model = WorkspaceUser


class WorkspaceFactory(BaseFactory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f"workspace-{n}")


class WorkspaceSyncFactory(BaseSyncFactory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f"workspace-{n}")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    username = factory.Sequence(lambda n: f"username-{n}")
    api_key = factory.Sequence(lambda n: f"api-key-{n}")
    password_hash = "$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw."


class UserSyncFactory(BaseSyncFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    username = factory.Sequence(lambda n: f"username-{n}")
    api_key = factory.Sequence(lambda n: f"api-key-{n}")
    password_hash = "$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw."


class OwnerFactory(UserFactory):
    role = UserRole.owner


class AdminFactory(UserFactory):
    role = UserRole.admin


class AnnotatorFactory(UserFactory):
    role = UserRole.annotator


class DatasetFactory(BaseFactory):
    class Meta:
        model = Dataset

    name = factory.Sequence(lambda n: f"dataset-{n}")
    distribution = {"strategy": DatasetDistributionStrategy.overlap, "min_submitted": 1}
    workspace = factory.SubFactory(WorkspaceFactory)


class RecordFactory(BaseFactory):
    class Meta:
        model = Record

    fields = {
        "text": "This is a text",
        "sentiment": "neutral",
    }
    external_id = factory.Sequence(lambda n: f"external-id-{n}")
    dataset = factory.SubFactory(DatasetFactory)


class ResponseFactory(BaseFactory):
    class Meta:
        model = Response

    record = factory.SubFactory(RecordFactory)
    user = factory.SubFactory(UserFactory)


class VectorSettingsFactory(BaseFactory):
    class Meta:
        model = VectorSettings

    name = factory.Sequence(lambda n: f"vector-{n}")
    title = "Vector Title"
    dimensions = factory.LazyAttribute(lambda _: random.randrange(16, 1024))
    dataset = factory.SubFactory(DatasetFactory)


class VectorFactory(BaseFactory):
    class Meta:
        model = Vector

    record = factory.SubFactory(RecordFactory)
    vector_settings = factory.SubFactory(VectorSettingsFactory)


class FieldFactory(BaseFactory):
    class Meta:
        model = Field

    name = factory.Sequence(lambda n: f"field-{n}")
    title = "Field Title"
    dataset = factory.SubFactory(DatasetFactory)


class TextFieldFactory(FieldFactory):
    settings = {
        "type": FieldType.text,
        "use_markdown": False,
    }


class ImageFieldFactory(FieldFactory):
    settings = {
        "type": FieldType.image,
    }


class ChatFieldFactory(FieldFactory):
    settings = {
        "type": FieldType.chat,
        "use_markdown": True,
    }


class MetadataPropertyFactory(BaseFactory):
    class Meta:
        model = MetadataProperty

    # TODO: Remove this method and fix possible failing tests
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        default_settings = getattr(cls, "settings", {})
        settings = kwargs.get("settings", {})
        if settings:
            new_settings = default_settings.copy()
            new_settings.update(settings)
            kwargs["settings"] = new_settings
        return super()._create(model_class, *args, **kwargs)

    name = factory.Sequence(lambda n: f"metadata-property-{n}")
    title = "Metadata property title"
    allowed_roles = [UserRole.admin, UserRole.annotator]
    dataset = factory.SubFactory(DatasetFactory)


class TermsMetadataPropertyFactory(MetadataPropertyFactory):
    settings = {"type": MetadataPropertyType.terms, "values": ["a", "b", "c"]}


class IntegerMetadataPropertyFactory(MetadataPropertyFactory):
    settings = {"type": MetadataPropertyType.integer}


class FloatMetadataPropertyFactory(MetadataPropertyFactory):
    settings = {"type": MetadataPropertyType.float}


class QuestionFactory(BaseFactory):
    class Meta:
        model = Question

    # TODO: Remove this method and fix possible failing tests
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        default_settings = cls.settings.copy()
        settings = kwargs.get("settings", {})
        if settings:
            new_settings = default_settings.copy()
            new_settings.update(settings)
            kwargs["settings"] = new_settings
        return super()._create(model_class, *args, **kwargs)

    name = factory.Sequence(lambda n: f"question-{n}")
    title = "Question Title"
    description = "Question Description"
    dataset = factory.SubFactory(DatasetFactory)
    settings = {}


class TextQuestionFactory(QuestionFactory):
    settings = {"type": QuestionType.text.value, "use_markdown": False}


class RatingQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.rating.value,
        "options": [
            {"value": 0},
            {"value": 1},
            {"value": 2},
            {"value": 3},
            {"value": 4},
            {"value": 5},
            {"value": 6},
            {"value": 7},
            {"value": 8},
            {"value": 9},
            {"value": 10},
        ],
    }


class LabelSelectionQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.label_selection.value,
        "options": [
            {"value": "option1", "text": "Option 1", "description": None},
            {"value": "option2", "text": "Option 2", "description": None},
            {"value": "option3", "text": "Option 3", "description": None},
        ],
    }


class MultiLabelSelectionQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.multi_label_selection.value,
        "options": [
            {"value": "option1", "text": "Option 1", "description": None},
            {"value": "option2", "text": "Option 2", "description": None},
            {"value": "option3", "text": "Option 3", "description": None},
        ],
        "options_order": OptionsOrder.natural,
    }


class RankingQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.ranking.value,
        "options": [
            {"value": "completion-a", "text": "Completion A", "description": None},
            {"value": "completion-b", "text": "Completion B", "description": None},
            {"value": "completion-c", "text": "Completion C", "description": None},
        ],
    }


class SpanQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.span.value,
        "field": "field-a",
        "visible_options": None,
        "options": [
            {"value": "label-a", "text": "Label A", "description": "Label A description"},
            {"value": "label-b", "text": "Label B", "description": "Label B description"},
            {"value": "label-c", "text": "Label C", "description": "Label C description"},
        ],
        "allow_overlapping": False,
        "allow_character_annotation": True,
    }


class SuggestionFactory(BaseFactory):
    class Meta:
        model = Suggestion

    record = factory.SubFactory(RecordFactory)
    question = factory.SubFactory(QuestionFactory)
    value = "negative"


class WebhookFactory(BaseFactory):
    class Meta:
        model = Webhook

    url = factory.Sequence(lambda n: f"https://example-{n}.com")
    events = [WebhookEvent.response_created]
